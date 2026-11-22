from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ApprovalDoc(Base):
    __tablename__ = "approval_docs"

    id = Column(Integer, primary_key=True, index=True)
    drafter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type = Column(String(30), nullable=False)  # VACATION, EXPENSE, SUPPLY
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)  # AI 3줄 요약
    ai_ocr_data = Column(JSONB, nullable=True)  # 영수증 OCR 추출 데이터
    status = Column(String(20), default="PENDING")  # PENDING, IN_PROGRESS, APPROVED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lines = relationship("ApprovalLine", back_populates="document", cascade="all, delete-orphan")


class ApprovalLine(Base):
    __tablename__ = "approval_lines"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("approval_docs.id", ondelete="CASCADE"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    step_order = Column(Integer, nullable=False)  # 1차, 2차 결재 순서
    status = Column(String(20), default="WAITING")  # WAITING, APPROVED, REJECTED
    comment = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    document = relationship("ApprovalDoc", back_populates="lines")