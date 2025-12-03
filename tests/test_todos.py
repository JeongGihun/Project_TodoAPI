# todo CRUD 테스트

def test_create_todo_success(auth_client) :
    """Todo 생성 성공 테스트"""
    response = auth_client.post('/todos', json = {
        'title' : 'Test Todo',
        'description' : 'Test Description'
    })

    assert response.status_code == 201
    assert response.json['data']['title'] == 'Test Todo'
    assert response.json['data']['user_id'] == 1

def test_create_todo_without_auth(client) :
    """인증 없이 Todo 생성 시도 테스트"""
    response = client.post('/todos', json = {
        'description' : 'Only description'
    })

    assert response.status_code == 401

def test_create_todo_missing_title(auth_client) :
    """제목 누락 테스트"""
    response = auth_client.post('/todos', json = {
        'description' : 'Only description'
    })

    assert response.status_code == 400

def test_get_todos(auth_client) :
    """Todo 목록 조회 테스트"""
    # Todo 2개 생성
    auth_client.post('/todos', json = {'title' : 'Todo 1'})
    auth_client.post('/todos', json = {'title' : 'Todo 2'})

    # 조회
    response = auth_client.get('/todos')

    assert response.status_code == 200
    assert response.json['count'] == 2
    assert len(response.json['data']) == 2

def test_get_todo_by_id(auth_client) :
    """특정 Todo 조회 테스트"""
    # Todo 생성
    create_response = auth_client.post('/todos', json = {'title' : 'Test Todo'})
    todo_id = create_response.json['data']['id']

    # 조회
    response = auth_client.get(f'/todos/{todo_id}')

    assert response.status_code == 200
    assert response.json['data']['title'] == 'Test Todo'

def test_update_todo(auth_client) :
    """Todo 수정 테스트"""
    # Todo 생성
    create_response = auth_client.post('/todos', json= {'title' : 'Original'})
    todo_id = create_response.json['data']['id']

    # 수정
    response = auth_client.put(f'/todos/{todo_id}', json = {
        'title' : 'Updated',
        'completed' : True
    })

    assert response.status_code == 200
    assert response.json['data']['title'] == 'Updated'
    assert response.json['data']['completed'] == True

def test_delete_todo(auth_client) :
    """Todo 삭제 테스트"""
    # Todo 생성
    create_response = auth_client.post('/todos', json = {'title':'To Delete'})
    todo_id = create_response.json['data']['id']

    # 삭제
    response = auth_client.delete(f'/todos/{todo_id}')

    assert response.status_code == 200

    # 조회 시도
    get_response = auth_client.get(f'/todos/{todo_id}')
    assert get_response.status_code == 404

def test_forbidden_access_other_user_todo(client) :
    """다른 사용자의 Todo 접근 테스트"""
    # User 1 생성 및 Todo 생성
    client.post('/register', json= {'username' : 'user1', 'email' : 'user1@test.com', 'password' : '1234'})
    login1 = client.post('/login', json = {'username' : 'user1', 'password' : '1234'})
    token1 = login1.json['access_token']

    create_response = client.post('/todos', json = {'title' : 'User1 Todo'},
                                  headers = {'Authorization' : f'Bearer {token1}'})
    todo_id = create_response.json['data']['id']

    # User 2 생성 및 User 1의 Todo 수정 시도
    client.post('/register', json = {'username':'user2', 'email' : 'user2@test.com', 'password': '1234'})
    login2 = client.post('/login', json = {'username' : 'user2', 'password' : '1234'})
    token2 = login2.json['access_token']

    response = client.put(f'/todos/{todo_id}',
                          json = {'title' : 'Hacked'},
                          headers = {'Authorization' : f'Bearer {token2}'})

    assert response.status_code == 403