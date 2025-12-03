# Todo API 프로젝트
Flask를 이용한 할 일 목록 만들기

## 개발 기간
- 2025_11

## 목적 
- Python 백엔드 학습 및 포트폴리오

## 주요기능
- 사용자 인증 (JWT, 해시)
- Todo CRUD
- 사용자별 Todo 관리
- DB 연동
- 보안 (Bcrypt, .env)

## 기술스택
- Python (dotnev, pytest...)
- Flask (SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt)
- SQLite
- Postman

## 주요 학습 내용
- RESTful API 설계
- JWT 토큰 기반 인증
- ORM (SQLAlchemy) 사용
- 1:N 관계 설정
- 단위 테스트 작성 (Pytest)

## 설치 및 실행
### 프로젝트 클론
  git clone <repository-url>
  cd todo-api
### 가상환경 생성 및 설치
  python -m venv venv
  venv\Scripts\activate
### 패키지 설치
  pip install -r requirements.txt
### 환경변수 설정
### 서버 실행
  python app.py
### 테스트
  pytest
  pytest tests/test_auth.py -v (특정 파일)
  pytest -v -s (상세 출력)

## 프로젝트 구조
'''
  todo-api/
  ├── app.py              # Flask 애플리케이션 메인
  ├── models.py           # 데이터베이스 모델 (User, Todo)
  ├── config.py           # 설정 파일
  ├── .env                # 환경 변수 (Git에 포함되지 않음)
  ├── .gitignore          # Git 제외 파일 목록
  ├── requirements.txt    # 패키지 의존성
  ├── todo.db             # SQLite 데이터베이스 파일
  ├── tests/              # 테스트 코드
  │   ├── conftest.py
  │   ├── test_auth.py
  │   └── test_todos.py
  └── README.md           # 프로젝트 문서
'''

## 테스트 파일 구조
'''
tests/
  ├── conftest.py      # 테스트 설정 (fixtures)
  ├── test_auth.py     # 회원가입/로그인 테스트
  └── test_todos.py    # Todo CRUD 테스트
'''

## API 명세
- API_DOCS.md 확인
