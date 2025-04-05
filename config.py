import os

from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
    # 데이터베이스 접속 주소 설정: SQLite 데이터베이스 사용, 데이터베이스 파일을 pybo.dp 파일로 저장
SQLALCHEMY_TRACK_MODIFICATIONS = False # SQLAlchemy 이벤트 처리 옵션(파이보에 필요 x)
SECRET_KEY = "dev" # 실제로는 dev같은 유추하기 쉬운 문자열은 위험함