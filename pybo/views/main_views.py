from flask import Blueprint, url_for
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/') # 'main': 블루프린트 별칭, url_prefix: url 접두어

@bp.route('/hello')
def hello_pybo():
    return 'Hello, Pybo!'

@bp.route('/')
def index():
    return redirect(url_for('question._list')) # question: 블루프린트 별칭, _list: 블루프린트에 등록된 함수명

# url_for: 라우팅 함수명으로 url을 찾는 함수(유지보수에 편리)
# redirect: 입력된 url로 리다이렉트