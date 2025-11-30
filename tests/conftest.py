# 테스트 설정

import pytest
from app import app, db
from models import User, Todo

@pytest.fixture
# 테스트에 필요한 준비물을 만드는 데코레이터
# 여기서는 client()를 client로, auth_client에 client 삽입
def client() :
    """테스트 Flask 클라이언트 생성"""
    app.config['Testing'] = True   # 테스트 모드 활성화. Flask 내장함수
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory' # 메모리 DB사용. 테스트 끝나면 자동 삭제

    with app.test_client() as client:
        with app.app_context() :
            db.create_all() # 테스트용 DB 테이블 생성
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_client(client) :
    """로그인 된 클라이언트 (+토큰)"""
    # 회원가입
    # Postman의 body에 넣는 값처럼 테스트용 DB
    client.post('/register', json={
        'username' : 'testuser',
        'email' : 'test@test.com',
        'password' : 'testpass'
    })

    # 로그인
    response = client.post('/login', json={
        'username' : 'testuser',
        'password' : 'testpass'
    })

    token = response.json['access_token']  # JWT 토큰 추출

    # 토큰을 헤더에 포함하는 헬퍼 클래스
    class AuthClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token

        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {self.token}'
            return self.client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {self.token}'
            return self.client.post(*args, **kwargs)

        def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {self.token}'
            return self.client.put(*args, **kwargs)

        def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {self.token}'
            return self.client.delete(*args, **kwargs)

    return AuthClient(client, token)