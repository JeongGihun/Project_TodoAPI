# 테스트 설정

import pytest
from app import app, db
from models import User, Todo

@pytest.fixture
# 테스트에 필요한 준비물을 만드는 데코레이터
# 여기서는 client()를 client로, auth_client에 client 삽입
def client() :
    """테스트 Flask 클라이언트 생성"""
    app.config['TESTING'] = True   # 테스트 모드 활성화. Flask 내장함수
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory' # 메모리 DB사용. 테스트 끝나면 자동 삭제

    with app.test_client() as client:
    # with app.test_client()가 반환되는 값을 client라 명
    # 컨텍스트 : 특정 코드가 실행되는 환경이나 상태
        with app.app_context() :
    # Flask에는 DB처럼 App context안에서만 접근 가능한 경우 존재. db.create_all() 하려면 필요
            db.create_all() # 테스트용 DB 테이블 생성
        yield client
    # yield 기준으로 테스트 시작 전 / 후로 나눔
        with app.app_context():
            db.drop_all()
    # 모든 테이블 삭제
    # with : 컨텍스트 관리
    # yield : 제너레이터 사용

@pytest.fixture
def auth_client(client) :
    """로그인 된 클라이언트 (+토큰)"""

    # DB 초기화 (중요!)
    with app.app_context():
        db.drop_all()
        db.create_all()


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
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.get(*args, **kwargs)
        # *args : 위치 인자 -> 튜플로 묶임(url)
        # **kwargs : 키워드 인자 -> dict로 묶임
        # headers 라는 키가 없으면 빈 dict 생성 및 반환, 있으면 기존 값 반환
        # 반환된 dict에 키-값 추가

        def post(self, *args, **kwargs):
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.post(*args, **kwargs)

        def put(self, *args, **kwargs):
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.put(*args, **kwargs)

        def delete(self, *args, **kwargs):
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.delete(*args, **kwargs)

    return AuthClient(client, token)