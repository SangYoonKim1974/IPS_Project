from fastapi import FastAPI

# FastAPI 애플리케이션 인스턴스 생성 (Swagger UI 제목 및 설명 설정)
app = FastAPI(
    title="inhouse-pm-system API",
    description="기업 내부 통합 관리 시스템 (사원·권한, 전자결재, 재고·자산, AI 업무 보조) 백엔드 API",
    version="0.1.0",
)


# 1. 기본 루트 엔드포인트 (서버 생존 확인용)
@app.get("/", tags=["System"])
def read_root():
    return {
        "status": "running",
        "project": "inhouse-pm-system",
        "message": "기업 내부 관리 시스템 API 서버가 정상 작동 중입니다!",
    }


# 2. 시스템 상태 체크 엔드포인트 (Health Check)
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "database": "pending"}