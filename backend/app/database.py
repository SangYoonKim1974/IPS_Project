import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# .env 파일에서 환경변수 불러오기
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경변수가 .env 파일에 설정되지 않았습니다.")

# SQLAlchemy DB 엔진 생성
engine = create_engine(DATABASE_URL)

# DB 세션을 생성하는 팩토리 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 DB 모델(테이블)이 상속받을 기본 클래스
Base = declarative_base()


# FastAPI API 요청마다 DB 세션을 열고, 요청이 끝나면 안전하게 닫아주는 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()