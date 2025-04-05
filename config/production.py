from config.default import *

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'\r\x1a\x97\xb2uv\x0b:zm\x89\xb9\xf9\xcf\xdbR'