from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# 1. 부서 관련 스키마
class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# 2. 사원 등록(회원가입) 요청 스키마
class UserCreate(BaseModel):
    emp_number: str          # 사번 (예: 2026001)
    email: EmailStr          # 이메일
    password: str            # 평문 비밀번호 (서버에서 암호화 저장)
    name: str                # 이름
    position: str            # 직급 (사원, 대리, 팀장 등)
    role: str = "USER"       # 권한 (ADMIN, MANAGER, USER)
    department_id: Optional[int] = None


# 3. 사원 정보 응답 스키마 (비밀번호 제외)
class UserResponse(BaseModel):
    id: int
    emp_number: str
    email: EmailStr
    name: str
    position: str
    role: str
    department_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 4. JWT 로그인 토큰 응답 스키마
class Token(BaseModel):
    access_token: str
    token_type: str