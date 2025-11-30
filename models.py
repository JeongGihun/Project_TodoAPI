from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model) :
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 나중에 해시화 작업 필요
    created_at = db.Column(db.DateTime, default=datetime.now)

    todos = db.relationship('Todo', backref='user', lazy=True, cascade='all, delete-orphan')
    # db.relationship은 실제 DB에 저장되지 않는 가상 연결통로
    # 매개 변수 : 연결할 모델명 / 역참조 생성 / 지연 로딩 여부 / 종속
    # 관계 설정 : 이 유저가 가진 모든 Todo
    # backref : 역참조 설정. 원래는 존재하지 않지만 가상으로 속성을 추가. 즉, 이름은 마음껏 바꿔도 됨
    # lazy = True : 필요할 때만 Todo 로드 (즉시 로딩과 비슷)
    # cascade = 'all, delete-orphan' : User 삭제되면 그 밑의 Todo 삭제


    def to_dict(self):
        """객체를 딕셔너리 형태로 전환 (비밀번호 제외)"""
        return {
            'id' : self.id,
            'username' : self.username,
            'email' : self.email,
            'created_at' : self.created_at.isoformat()
        }

class Todo(db.Model) :
    __tablename__ = 'todos'   # table명 선언

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 외래키 추가, 해당 Todo를 만들 User의 id

    def to_dict(self):
        """객체를 딕셔너리 형태로 전환(JSON 응답용)"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),  # datetime 객체는 JSON으로 직렬화가 불가해 변경
            'updated_at': self.updated_at.isoformat()
        }