from datetime import datetime

from dns.asyncresolver import reset_default_resolver
from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.models import Question, Answer, User
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question') # 'main': 블루프린트 별칭, url_prefix: url 접두어

@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1) # 페이지
        # GET 방식으로 요청한 URL에서 page 값을 가져옴
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc()) # 최근 게시글부터 정렬
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
        .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
        .join(User) \
        .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
        .filter(Question.subject.ilike(search) | # 질문제목
                Question.content.ilike(search) | # 질문내용
                User.username.ilike(search) | # 질문작성자
                sub_query.c.content.ilike(search) | # 답변내용
                sub_query.c.username.ilike(search) # 답변작성자
                ) \
        .distinct() # question id 중복 방지
    question_list = question_list.paginate(page=page, per_page=10) # page: 현재 조회할 페이지 번호, per_page: 페이지 당 게시물 수
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)

@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id) # 해당 question_id를 가진 레코드(행)을 가져옴
    return render_template('question/question_detail.html', question=question, form=form)

@bp.route('/create/', methods=('GET', 'POST')) # GET, POST 두 가지 방법 다 가능
@login_required # 함수명 바로 위에 위치해 있어야 함(라우팅 함수가 호출되면 이 함수가 먼저 실행
def create():
    form = QuestionForm()
    # post 방식 요청일 때 데이터베이스에 질문을 저장(저장하기 버튼)
    if request.method == 'POST' and form.validate_on_submit():
        # form.validate_on_submit: 전송된 폼 데이터의 정합성 점검
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    # get 방식 요청일 때 질문 등록 화면을 보여줌(질문등록 버튼)
    return render_template('question/question_form.html', form=form)

@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id) # 기본키가 동일한 객체 조회
    if g.user != question.user:
        flash('수정권한이 없습니다') # 강제로 오류 발생. 로직에 오류가 있을 때만 사용
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST': # POST 요청(저장하기 버튼을 눌렀을 때)
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question) # form 변수에 들어 있는 데이터(화면에서 입력)를 question 객체에 업데이트
            question.modify_date = datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else: # GET 요청(질문 수정 버튼을 눌렀을 때)
        form = QuestionForm(obj=question) # 조희한 데이터를 매개변수로 전달하여 폼 생성
    return render_template('question/question_form.html', form=form)

@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    _question = Question.query.get_or_404(question_id)
    if g.user == _question.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
    else:
        _question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=_question.id))

# 각각의 form을 먼저 선언하는 이유는 csrf 보호, 폼 검증, 유지보수성 측면에서 비효율적이므로, 뷰에서 폼을 생성함