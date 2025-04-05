from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm
from pybo.models import User

import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup/', methods=('GET', 'POST')) # POST방식: 계정 저장, GET방식:계정 등록
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                            # generate_password_hash: 암호화함수, 암호화한 데이터는 복호화할 수 없음
                        email=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자입니다.')
            # flash: 프로그램 논리 오류를 발생시키는 함수(필드 자체 오류 x)
    return render_template('auth/signup.html', form=form)

@bp.route('/login/', methods=('GET', 'POST')) # GET: 로그인 화면을 보여줌, POST: 로그인 수행
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear() # 기존 세션 데이터 삭제
            session['user_id'] = user.id # 현재 로그인한 user의 id를 세션에 저장하여 로그인 상태 유지
            _next = request.args.get('next', '') # next가 있으면 반환, 없으면 '' 반환
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)

# 로그인되어 있는지 확인(로그인 되어 있으면 세션에 user_id로 저장되어 있음)
@bp.before_app_request # 라우팅 함수보다 항상 먼저 실행
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

# 로그아웃
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# 로그인이 안되어 있으면 로그인 화면 -> 로그인 완료 -> 기존 페이지로 이동
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
                # get방식이면 현재 링크, 아니면 공백을 저장
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view