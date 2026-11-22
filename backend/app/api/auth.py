from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    require_roles,
    verify_password,
)
from app.database import get_db
from app.models.user import Department, User
from app.schemas.user import (
    DepartmentCreate,
    DepartmentResponse,
    Token,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Auth & Users (사원·권한)"])


# 1. 부서 등록 API
@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    existing = db.query(Department).filter(Department.name == dept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 부서명입니다.")
    new_dept = Department(name=dept.name)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept


# 2. 사원 등록 (회원가입) API
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    if db.query(User).filter(User.emp_number == user_in.emp_number).first():
        raise HTTPException(status_code=400, detail="이미 등록된 사원번호입니다.")
    if user_in.role not in ["ADMIN", "MANAGER", "USER"]:
        raise HTTPException(status_code=400, detail="권한(role)은 ADMIN, MANAGER, USER 중 하나여야 합니다.")

    new_user = User(
        emp_number=user_in.emp_number,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        name=user_in.name,
        position=user_in.position,
        role=user_in.role,
        department_id=user_in.department_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 3. 로그인 및 JWT 토큰 발급 API (username 칸에 이메일 입력)
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화(퇴사) 처리된 계정입니다.")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


# 4. 내 정보 조회 API (로그인한 모든 사용자 가능)
@router.get("/me", response_model=UserResponse)
def read_my_info(current_user: User = Depends(get_current_user)):
    return current_user


# 5. 전체 사원 목록 조회 API (RBAC 테스트: ADMIN 또는 MANAGER만 조회 가능!)
@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "MANAGER"])),
):
    return db.query(User).all()