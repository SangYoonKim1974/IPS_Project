from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import models
from app.api import auth
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="inhouse-pm-system API",
    description="기업 내부 통합 관리 시스템 (사원·권한, 전자결재, 재고·자산, AI 업무 보조) 백엔드 API",
    version="0.1.0",
)

# 사원·권한 API 라우터 등록
app.include_router(auth.router)


@app.get("/", tags=["System"])
def read_root():
    return {
        "status": "running",
        "project": "inhouse-pm-system",
        "message": "기업 내부 관리 시스템 API 서버가 정상 작동 중입니다!",
    }


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected (PostgreSQL - inhouse_pm_system)",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 연결 실패: {str(e)}")