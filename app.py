from flask import Flask, request, jsonify  # json : 데이터를 주고 받을때 사용하는 텍스트
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Todo, User
from config import Config
# Bcrpyt : 비밀번호 암호화, 해싱 알고리즘 사용 + 같은 비밀번호도 매번 다른 해시값!
# 암호화 방법에는 argon2, PBKDF2 등이 있지만 가장 대중적인 암호화 방법 사용
# flask_jwt_extended : 토큰 기반 인증
# 비밀번호 -> 암호화 -> 확인 -> 인가 -> JWT로 로그인 이후 인증 상태 유지. 참고로 JWT는 서버에 세션 저장 X

app = Flask(__name__)
app.config.from_object(Config)  # from_object : Config 클래스의 속성을 읽어 config 딕셔너리에 삽입(원래 존재)

# SQLAlchemy 초기화
db.init_app(app)  # db는 앞으로 app(app.py에서 생성한 객체)와 연동되라는 의미
bcrypt = Bcrypt(app) # 비밀번호 암호화
jwt = JWTManager(app) # JWT 토큰 관리

# DB 테이블 생성
# app의 설정을 사용해 DB 생성
# create_all은 DB에 테이블을 자동으로 생성하게 하는 메서드
# with은 사용 후에 자동으로 소멸시켜주는 역할
# .app_context는 Flask의 컨텍스트(문맥) 안에서 코드를 실행하겠다는 의미
with app.app_context():
    db.create_all()

# 루트 경로(기본 페이지)
@app.route('/')
def home() :
    return jsonify({
        'message' : 'TodoAPI에 오신 것을 환영합니다.',
        'version' : '1.0',
        'endpoints' : {
            'GET /' : 'API 정보 조회',
            'POST /todos' : '할 일 추가',
            'GET /todos' : '할 일 목록 조회',
            'GET /todos/<id>' : '특정 할 일 조회',
            'PUT /todos/<id>' : '할 일 수정',
            'DELETE /todos/<id>' : '할 일 삭제'
        }
    })
# Python은 딕셔너리 형식을 return 불가
# 따라서 json 형식으로 출력
# JSON(JavaScript Object Notation) : 데이터를 텍스트로 표현하는 방식
# JSON을 쓰는 이유 : 모든 언어 사용 가능, 가벼움, 읽기 쉬움 -> 현대 웹 개발에선 대다수가 JSON 사용
# JSON 대체 가능한 것 : XML, CSV

# 회원가입
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # 입력 전송
        if not data:
            return jsonify({'error' : 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        # 필드 확인
        if not username or not email or not password :
            return jsonify({'error' : 'username, email, password are required'}), 400

        # 중복 확인
        if User.query.filter_by(username=username).first():
            return jsonify({'error' : 'Username already exists'}), 400
        # User 쿼리의 username 속성명에서 지역변수 'username'과 일치하는 부분이 있는지 확인
        # first는 중복된 것이 하나라도 있으면 안되기 때문

        if User.query.filter_by(email=email).first() :
            return jsonify({'error' : 'Email already exists'}), 400

        # 비밀번호 해쉬화
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # bcrypt 알고리즘으로 해싱. bytes를 문자열로 전환
        # 순서 : 클라이언트에서 비번 입력 -> HTTPS로 전송시 암호화 -> 서버 수신 받으면서 복호화(다시 평문) -> 서버에서 해싱

        # 새 User 생성
        new_user = User(
            username = username,
            email = email,
            password = hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message' : '회원가입 완료',
            'data' : new_user.to_dict()
        }), 201

    except Exception as e :
        db.session.rollback()
        return jsonify({'error' : 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    try :
        data = request.get_json()

        if not data :
            return jsonify({'error' : 'No data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error' : 'username and password are required'}), 400

        # 사용자 조회
        user = User.query.filter_by(username=username).first()

        # 사용자 없거나 비밀번호 틀림
        if not user or not bcrypt.check_password_hash(user.password, password) :
            return jsonify({'error' : 'Invalide username or password'}), 401
        # check_password_hash() : 비밀번호 검증

        # JWT 토큰 생성, user_id포함
        # user_id를 str 형식으로 변경해서 받음. 안하면 로그인 과정에서 422에러
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message' : '로그인 성공',
            'access_token' : access_token,
            'user' : user.to_dict()
        }), 200

    except Exception as e :
        return jsonify({'error' : 'Internal server error'}), 500

# Create
@app.route('/todos', methods=['POST'])  # todos라는 url로 메서드가 post면 해당 함수 실행
# 인증 필요. 토큰 없으면 에러
@jwt_required()
def create_todo() :
    try :
        # 로그인한 사용자 ID 가져오기, JWT 토큰에 포함된 ID를 가져온다는 의미
        user_id = get_jwt_identity()

        # 클라이언트가 보낸 JSON 데이터 파싱
        # JSON 형식 데이터 -> Python의 딕셔너리 형식으로 변환
        data = request.get_json()

        # 입력 검증
        if not data :
            return jsonify({
                'error' : 'No data provided',
                'message' : '데이터를 입력해주세요.'
            }), 400
        # data가 없으면, 400 에러 발생
        # 또한 return 뒤에 그냥 숫자가 붙는 이유는, Flask 특성 상 return 전체를 튜플로 해석해서 괄호가 있는 것처럼 해석
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        # data['title'] / data['description']의 값을 가져옮. 없으면 default값은 ''이며, 혹시 모르니 양쪽 빈 칸 제거

        if not title :
            return jsonify({
                'error' : 'Title is required',
                'message' : '할 일 제목을 입력해주세요.'
            }), 400
        # 제목이 비어있으면 에러

        if len(title) > 100 :
            return jsonify({
                'error' : 'Title too long',
                'message' : '제목은 100자 이내로 입력해주세요.'
            }), 400
        # 제목 길이 100 초과하면 에러

        # 새 Todo 객체 생성
        new_todo = Todo(
            title = title,
            description = description,
            user_id = user_id
        )

        db.session.add(new_todo)  # db.session은 일종의 자료구조 + 관리시스템
        db.session.commit()

        return jsonify({
            'message' : '할 일이 추가되었습니다.',
            'data' : new_todo.to_dict()
        }), 201
        # 완료되면 201 상태 코드. 리소스 생성 성공했다는 의미

    except Exception as e :
        db.session.rollback()
        return jsonify({
            'error' : 'Internal server error',
            'message' : '서버 오류가 발생했습니다.'
        }), 500
    # 예상치 못한 에러 발생 시 500 에러 반환

# Read / 전체 할 일 목록
@app.route('/todos', methods=['GET'])
@jwt_required()
def get_todos() :
    user_id = get_jwt_identity()

    todos = Todo.query.filter_by(user_id = user_id).all()  # Todo의 전체 불러오기

    return jsonify({
        'message' : '할 일 목록 조회 성공',
        'count' : len(todos),
        'data' : [todo.to_dict() for todo in todos]
    }), 200

# Read / 특정 할 일 목록
@app.route('/todos/<int:todo_id>', methods = ['GET'])
@jwt_required()
def get_todo(todo_id) :
    user_id = get_jwt_identity()

    todo = Todo.query.get(todo_id)

    if not todo :
        return jsonify({
            'error' : 'Not Found',
            'message' : f'ID {todo_id}인 할 일을 찾을 수 없습니다.'
        }), 404

    # 자기의 할 일인지 구분
    if todo.user_id != user_id :
        return jsonify({
            'error' : 'Forbidden',
            'message' : '다른 사용자의 할 일입니다.'
        }), 403

    return jsonify({
        'message' : '할 일 조회 성공',
        'data' : todo.to_dict()
    }), 200

# Update
@app.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id) :
    try :
        user_id = get_jwt_identity()

        todo = Todo.query.get(todo_id)

        if not todo :
            return jsonify({
                'error' : 'No data',
                'message' : f'ID {todo_id}인 할 일을 찾을 수 없습니다.'
            }), 404

        # 자기의 할 일인지 확인
        if todo.user_id != user_id :
            return jsonify({
                'error': 'Forbidden',
                'message': '다른 사용자의 할 일입니다.'
            }), 403

        data = request.get_json()

        if not data :
            return jsonify({
                'error' : 'No data',
                'message' : '수정할 데이터를 입력해주세요.'
            }), 400

        # 제목 수정
        if 'title' in data :
            title = data['title'].strip()
            if not title :
                return jsonify({
                    'error' : 'Title is required',
                    'message' : '제목은 비울 수 없습니다.'
                }), 400

            if len(title) > 100 :
                return jsonify({
                    'error' : 'Title too long',
                    'message' : '제목은 100글자 이내로 입력해주세요.'
                }), 400
            todo.title = title

        if 'description' in data :
            todo.description = data['description'].strip()

        if 'completed' in data :
            if not isinstance(data['completed'], bool) :
            # isinstance : input되는 값이 뒤의 형식이 아니면
                return jsonify({
                    'error' : 'Invalid data type',
                    'message' : 'completed는 true 혹은 false만 가능합니다.'
                }), 400
            todo.completed = data['completed']

        db.session.commit()

        return jsonify({
            'message' : '할 일이 수정되었습니다.',
            'data' : todo.to_dict()
        }), 200

    except Exception as e :
        db.session.rollback()
        return jsonify({
            'error' : 'Internal server error',
            'message' : '서버 오류가 발생했습니다.'
        }), 500
    # Create, Update는 위험해서 추가. 원래는 모든 부분에 추가 필요

# Delete
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id) :
    try :
        user_id = get_jwt_identity()

        todo = Todo.query.get(todo_id)

        if not todo :
            return jsonify({
                'error' : 'Not Found',
                'message' : f'ID {todo_id}인 할 일을 찾을 수 없습니다.'
            }), 404

        # 자기의 할 일인지 확인
        if todo.user_id != user_id :
            return jsonify({
                'error' : 'Forbidden',
                'message' : '다른 사용자의 할 일입니다.'
            }), 403

        deleted_todo = todo.to_dict()
        db.session.delete(todo)
        db.session.commit()

        return jsonify({
            'message' : '할 일이 삭제되었습니다.',
            'data' : deleted_todo
        }), 200

    except Exception as e :
        db.session.rollback()
        return jsonify({
            'error' : 'Internal server error',
            'message' : '서버 오류가 발생했습니다.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 5000)

# HTTP 상태 코드
# 200 : 성공 (조회, 수정, 삭제)
# 201 : 성공 (생성)
# 400 : 클라이언트 요청 오류 (누락, 오류, 실패 등)
# 401 : 로그인 필요
# 403 : 요청은 이해했으나, 권한이 없어 거부함
# 404 : 리소스를 찾을 수 없음 (존재 X)
# 500 : 서버 내부 오류 (예상치 못한 부분)