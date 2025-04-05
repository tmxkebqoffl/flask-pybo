from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import AnswerForm
from pybo.models import Question, Answer
from .auth_views import login_required

bp = Blueprint('answer', __name__, url_prefix='/answer')

@bp.route('/create/<int:question_id>', methods=('POST',))
@login_required # 함수명 바로 위에 있어야 함
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    if form.validate_on_submit():
        content = request.form['content'] # 전송된 데이터 중 name이 content인 값
        answer = Answer(content=content, create_date=datetime.now(), user=g.user)
        question.answer_set.append(answer)
        # answer = Answer(question=question, content=content, create_date=datetime.now())
        # db.session.add(answer) 이렇게 하는 것도 괜츈
        db.session.commit()
        return redirect('{}#answer_{}'.format(
            url_for('question.detail', question_id=question.id), answer.id))
        # 첫번째 {}: 질문 상세 페이지 url, 두 번째 {}: 답변의 ID
        # #answer_{}: 웹 페이지 내의 특정 위치(앵커)로 이동하기 위한 장치
    return render_template('question/question_detail.html', question=question, form=form)

@bp.route('/modify/<int:answer_id>', methods=('GET', 'POST'))
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user != answer.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer.question.id))
    if request.method == "POST": # 저장하기 버튼
        form = AnswerForm()
        if form.validate_on_submit():
            form.populate_obj(answer) # form 변수에 들어 있는 데이터(화면에서 입력)를 answer 객체에 업데이트
            answer.modify_date = datetime.now() # 수정일시 저장
            db.session.commit()
            return redirect('{}#answer_{}'.format(
                url_for('question.detail', question_id=answer.question.id), answer.id))
    else: # 답변 수정 버튼
        form = AnswerForm(obj=answer) # 조희한 데이터를 매개변수로 전달하여 폼 생성
    return render_template('answer/answer_form.html', form=form)

@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question.id
    if g.user != answer.user:
        flash('삭제권한이 없습니다')
    else:
        db.session.delete(answer)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))

@bp.route('/vote/<int:answer_id>/')
@login_required
def vote(answer_id):
    _answer = Answer.query.get_or_404(answer_id)
    if g.user == _answer.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
    else:
        _answer.voter.append(g.user)
        db.session.commit()
    return redirect('{}#answer_{}'.format(
        url_for('question.detail', question_id=_answer.question.id), _answer.id))
# reqeust 객체: 생산 과정 없이 사용할 수 있는 기본 객체
#               브라우저의 요청부터 응답까지의 처리 구간에서 사용