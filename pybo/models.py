from pybo import db

question_voter = db.Table(
    'question_voter',
    # 사용자 아이디와 질문 이이디를 다중 기본키로 설정해서 다중 추천(투표)이 안 되게 함
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)

answer_voter = db.Table(
    'answer_voter',
    # 사용자 아이디와 답변 이이디를 다중 기본키로 설정해서 다중 추천(투표)이 안 되게 함
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), primary_key=True)
)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 기본키: 값이 자동으로 증가함(세팅x: 1씩 증가)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False) # Text: 글자 수 제한 불가 텍스트
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
        # user_id 속성을 새로 추가할 때... nullable=True, server_default='1')에서..
        # server_default: 기존 null 데이터에도 기본값 생성, default: 새로 생성되는 데이터만 기본값 생성
    user = db.relationship('User', backref=db.backref('question_set'))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter = db.relationship('User', secondary=question_voter, backref=db.backref('question_voter_set'))
    # 'User': 관계를 맺을 모델 클래스 이름, secondary=question_voter: 중간 연결 테이블 지정(N:N 관계를 위한 테이블)
    # backref: User 모델에 자동으로 추가될 역참조 속성 정의(해당 사용자가 '추천'한 모든 질문 목록에 접근 가능)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'))
        # ondelete=: 삭제 연동 설정(쿼리를 이용한 삭제에만 해당, 파이썬 코드로 삭제시 연동 x), 'CASCADE': 질문 삭제 -> 답변 삭제
    question = db.relationship('Question', backref=db.backref('answer_set'))
        # 첫 번째 파라미터: 참조할 모델명, 두 번째 backref 파라미터: 역참조(해당 질문에 대한 답변들(answer_set))
        # 파이썬 코드로 삭제할 때 연결된 모든 답변 삭제: backref=db.backref('answer_set', cascade='all, delete-orphan'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('answer_set'))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter = db.relationship('User', secondary=answer_voter, backref=db.backref('answer_voter_set'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)