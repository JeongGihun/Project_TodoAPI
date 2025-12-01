# 회원가입, 로그인 테스트
# 동작방법 : test_register_success 함수 발견 -> 매개변수 client 확인 -> @pytest.fixture로 선언된 client 함수 가져오기
#           -> client_fixture 실행 -> 반환값 받기 -> test_register_success 반환값 호출
# pytest를 실행할 경우 test_로 시작하는 함수를 찾아 실행한다.
# 원래대로라면 def를 선언한다고 해서 실행되지는 않지만, pytest 사용법임
def test_register_success(client) :
    """회원가입 성공 테스트"""
    response = client.post('/register', json = {
        'username' : 'newuser',
        'email' : 'new@test.com',
        'password' : '1234'
    })
    # Flask에서 가져오는 함수

    assert response.status_code == 201
    # assert는 이게 참이여야 한다는 검증문
    # 해당 조건이 True여야 통과하며, 안된다면 AssertionError 발생
    assert '회원가입 완료' in response.json['message']
    assert response.json['data']['username'] == 'newuser'

def test_register_duplicate_username(client) :
    """중복 username 테스트"""
    # 첫번째 회원가입
    client.post('/register', json = {
        'username' : 'testuser',
        'email' : 'test1@test.com',
        'password' : '1234'
    })

    # 같은 username으로 재가입 시도
    response = client.post('/register', json = {
        'username': 'testuser',
        'email': 'test1@test.com',
        'password': '1234'
    })

    assert response.status_code == 400
    assert 'already exists' in response.json['error']

def test_register_missing_fields(client) :
    """필수 필드 누락 테스트"""
    response = client.post('/register', json = {
        'username' : 'testuser',
        # email, password 누락
    })

    assert response.status_code == 400
    assert 'required' in response.json['error']

def test_login_success(client) :
    """로그인 성공 테스트"""
    # 회원가입
    client.post('/register', json = {
        'username' : 'testuser',
        'email' : 'test@test.com',
        'password' : '1234'
    })

    # 로그인
    response = client.post('/login', json = {
        'username' : 'testuser',
        'password' : '1234'
    })

    assert response.status_code == 200
    assert '로그인 성공' in response.json['message']
    assert 'access_token' in response.json

def test_login_wrong_password(client) :
    """잘못된 비밀번호 테스트"""
    # 회원가입
    client.post('/register', json = {
        'username' : 'testuser',
        'email' : 'test@test.com',
        'password' : '1234'
    })

    # 잘못된 비밀번호로 로그인
    response = client.post('/login', json = {
        'username' : 'testuser',
        'password' : 'wrong'
    })

    assert response.status_code == 401
    assert 'Invalid' in response.json['error']

def test_login_nonexistent_user(client) :
    """존재하지 않는 사용자 로그인 테스트"""
    response = client.post('/login', json = {
        'username' : 'nonexistent',
        'password' : '1234'
    })

    assert response.status_code == 401