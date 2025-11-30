import os
from datetime import timedelta  # timedelta : 시간 확인해주는 모듈
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()  # .env 파일 읽기

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 현재 config파일이 있는 디렉토리 경로를 절대 경로로 변환

    # 환경 변수에서 읽기
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, os.getenv("DATABASE_NAME", "todo.db"))}'
    # sqlite:/// -> DB를 SQLite 형식으로 변환, 경로 변환한 곳에 todo.db를 생성하겠다는 의미
    # os.getnev -> .env에서 입력값 1을 찾는다. 있으면 복사, 없으면 입력값 2 반환
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 객체 변경 추적 기능 비활성화. 대부분 불필요

    # JWT 설정 추가
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-do-not-use-in-production')      # JMT 인증
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')   # JWT 전용키
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))   # 토큰 유효기간 : 1시간
