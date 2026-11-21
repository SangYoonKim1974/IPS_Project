# 🏢 inhouse-pm-system (IPS_기업 내부 통합 관리 시스템)

실제 중소·중견기업의 실무 프로세스를 반영하여 개발한 **기업 내부 관리 시스템(ERP/그룹웨어)**입니다.
엑셀 및 수기 결재로 이루어지던 비효율적인 사내 업무를 디지털화하고, 직급별 권한 통제와 데이터 무결성을 보장하는 것을 목표로 합니다.

## 📌 프로젝트 개요
- **프로젝트 목적:** 실제 업체 도입용 실무 시스템 구축 및 백엔드 중심 포트폴리오
- **개발 인원:** 1인 개발 (기획·설계·개발·배포 전 과정 수행)
- **개발 기간:** 4주 (주차별 MVP 단계적 구현)

## 🛠 기술 스택 (Tech Stack)
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (ORM), Pydantic
- **Database:** PostgreSQL
- **Auth & Security:** JWT (Access/Refresh Token), Bcrypt (비밀번호 암호화), RBAC (역할 기반 접근 제어)
- **Frontend:** HTML/JS + Jinja2 템플릿 (또는 React/Bootstrap 기반 Admin 템플릿 - *추후 확정*)
- **Docs & DevOps:** Swagger UI (FastAPI 자동 생성), Docker, Git/GitHub

## 📂 문서 아카이브 (`docs/`)
- [01. 요구사항 정의서 및 4주 개발 로드맵(WBS)](./docs/01-requirements.md)
- `02. 데이터베이스 설계 (ERD & DDL)` *(예정)*
- `03. REST API 명세서` *(예정)*
