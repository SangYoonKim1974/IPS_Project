from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# 1. 품목(소모품/고정자산) 등록 요청 스키마
class InventoryCreate(BaseModel):
    item_type: str = Field(..., description="CONSUMABLE(소모품) 또는 ASSET(고정자산)")
    item_code: str = Field(..., description="품목/시리얼 코드 (예: PAPER-A4, LAPTOP-001)")
    name: str = Field(..., description="품목명")
    quantity: int = Field(default=0, ge=0, description="초기 수량 (0 이상)")
    min_stock: int = Field(default=5, ge=0, description="안전 재고 기준 수량")


# 2. 품목 정보 응답 스키마
class InventoryResponse(BaseModel):
    id: int
    item_type: str
    item_code: str
    name: str
    quantity: int
    min_stock: int
    assigned_user_id: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# 3. 입출고(IN/OUT) 트랜잭션 요청 스키마
class StockTransactionRequest(BaseModel):
    action_type: str = Field(..., description="IN(입고) 또는 OUT(출고/불출)")
    amount: int = Field(..., gt=0, description="변동 수량 (1 이상의 양수)")
    reason: Optional[str] = Field(default=None, description="입출고 사유")


# 4. 고정자산 지급/반납(ASSIGN/RETURN) 요청 스키마
class AssetAssignRequest(BaseModel):
    action_type: str = Field(..., description="ASSIGN(지급) 또는 RETURN(반납)")
    target_user_id: Optional[int] = Field(default=None, description="지급받을 사원 ID (지급 시 필수)")
    reason: Optional[str] = Field(default=None, description="지급/반납 사유")


# 5. 입출고 변동 이력 응답 스키마
class InventoryLogResponse(BaseModel):
    id: int
    item_id: int
    user_id: int
    action_type: str
    change_amount: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True