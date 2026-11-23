from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_roles
from app.database import get_db
from app.models.inventory import AssetInventory, InventoryLog
from app.models.user import User
from app.schemas.inventory import (
    AssetAssignRequest,
    InventoryCreate,
    InventoryLogResponse,
    InventoryResponse,
    StockTransactionRequest,
)

router = APIRouter(prefix="/api/inventory", tags=["Inventory & Assets (재고·자산)"])


# 1. 신규 품목(소모품/고정자산) 등록 API (ADMIN, MANAGER 권한 필요)
@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    item_in: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "MANAGER"])),
):
    if item_in.item_type not in ["CONSUMABLE", "ASSET"]:
        raise HTTPException(status_code=400, detail="item_type은 CONSUMABLE 또는 ASSET이어야 합니다.")

    if db.query(AssetInventory).filter(AssetInventory.item_code == item_in.item_code).first():
        raise HTTPException(status_code=400, detail="이미 등록된 품목/자산 코드입니다.")

    # 고정자산(ASSET)은 기본 수량 1로 세팅
    initial_qty = 1 if item_in.item_type == "ASSET" else item_in.quantity

    new_item = AssetInventory(
        item_type=item_in.item_type,
        item_code=item_in.item_code,
        name=item_in.name,
        quantity=initial_qty,
        min_stock=0 if item_in.item_type == "ASSET" else item_in.min_stock,
        status="AVAILABLE",
    )
    db.add(new_item)
    db.flush()  # DB에 임시 반영하여 new_item.id 확보

    # 초기 수량이 있으면 입고 이력(Log) 자동 기록
    if initial_qty > 0:
        init_log = InventoryLog(
            item_id=new_item.id,
            user_id=current_user.id,
            action_type="IN",
            change_amount=initial_qty,
            reason="신규 품목 초기 등록",
        )
        db.add(init_log)

    db.commit()
    db.refresh(new_item)
    return new_item


# 2. 전체 품목 및 부족 재고 필터링 조회 API (로그인한 모든 사원 조회 가능)
@router.get("", response_model=List[InventoryResponse])
def get_inventory_items(
    low_stock_only: bool = Query(default=False, description="True면 안전 재고 이하 부족 품목만 조회"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AssetInventory)
    if low_stock_only:
        query = query.filter(
            AssetInventory.item_type == "CONSUMABLE",
            AssetInventory.quantity <= AssetInventory.min_stock,
        )
    return query.order_by(AssetInventory.id.asc()).all()


# 3. 소모품 입고/출고(IN/OUT) 트랜잭션 API (마이너스 재고 방지 및 이력 기록)
@router.post("/{item_id}/transaction", response_model=InventoryResponse)
def process_stock_transaction(
    item_id: int,
    tx_in: StockTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if tx_in.action_type not in ["IN", "OUT"]:
        raise HTTPException(status_code=400, detail="action_type은 IN 또는 OUT이어야 합니다.")

    # 입고(IN)는 관리자/팀장만 가능하도록 권한 제어
    if tx_in.action_type == "IN" and current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="재고 입고 처리는 ADMIN 또는 MANAGER 권한이 필요합니다.")

    # with_for_update()로 행 잠금(Row Lock)을 걸어 동시 출고 시 재고 무결성 보장
    item = db.query(AssetInventory).filter(AssetInventory.id == item_id).with_for_update().first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 품목을 찾을 수 없습니다.")
    if item.item_type != "CONSUMABLE":
        raise HTTPException(status_code=400, detail="고정자산(ASSET)은 입출고가 아닌 지급/반납 API를 사용하세요.")

    if tx_in.action_type == "IN":
        item.quantity += tx_in.amount
        change = tx_in.amount
    else:  # OUT (출고/불출)
        if item.quantity < tx_in.amount:
            raise HTTPException(
                status_code=400,
                detail=f"재고가 부족하여 출고할 수 없습니다. (현재 재고: {item.quantity}, 요청 수량: {tx_in.amount})",
            )
        item.quantity -= tx_in.amount
        change = -tx_in.amount

    log = InventoryLog(
        item_id=item.id,
        user_id=current_user.id,
        action_type=tx_in.action_type,
        change_amount=change,
        reason=tx_in.reason,
    )
    db.add(log)
    db.commit()
    db.refresh(item)
    return item


# 4. 고정자산 지급/반납(ASSIGN/RETURN) API (ADMIN, MANAGER 권한 필요)
@router.post("/{item_id}/assign", response_model=InventoryResponse)
def assign_or_return_asset(
    item_id: int,
    req: AssetAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "MANAGER"])),
):
    if req.action_type not in ["ASSIGN", "RETURN"]:
        raise HTTPException(status_code=400, detail="action_type은 ASSIGN 또는 RETURN이어야 합니다.")

    item = db.query(AssetInventory).filter(AssetInventory.id == item_id).with_for_update().first()
    if not item:
        raise HTTPException(status_code=404, detail="해당 자산을 찾을 수 없습니다.")
    if item.item_type != "ASSET":
        raise HTTPException(status_code=400, detail="소모품(CONSUMABLE)이 아닌 고정자산(ASSET)만 지급/반납할 수 있습니다.")

    if req.action_type == "ASSIGN":
        if item.status == "IN_USE":
            raise HTTPException(status_code=400, detail="이미 다른 사원에게 지급되어 사용 중인 자산입니다.")
        if not req.target_user_id:
            raise HTTPException(status_code=400, detail="지급받을 사원 ID(target_user_id)를 입력해야 합니다.")

        target_user = db.query(User).filter(User.id == req.target_user_id, User.is_active == True).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="지급 대상 사원을 찾을 수 없습니다.")

        item.assigned_user_id = target_user.id
        item.status = "IN_USE"
        item.quantity = 0
        change = -1
        log_reason = req.reason or f"{target_user.name}({target_user.emp_number}) 사원에게 자산 지급"

    else:  # RETURN (반납)
        if item.status != "IN_USE":
            raise HTTPException(status_code=400, detail="현재 사용 중인 자산이 아니므로 반납 처리할 수 없습니다.")

        prev_user_id = item.assigned_user_id
        item.assigned_user_id = None
        item.status = "AVAILABLE"
        item.quantity = 1
        change = 1
        log_reason = req.reason or f"사원(ID:{prev_user_id})으로부터 자산 반납 완료"

    log = InventoryLog(
        item_id=item.id,
        user_id=current_user.id,
        action_type=req.action_type,
        change_amount=change,
        reason=log_reason,
    )
    db.add(log)
    db.commit()
    db.refresh(item)
    return item


# 5. 전체 입출고·지급 이력(Audit Log) 조회 API
@router.get("/logs", response_model=List[InventoryLogResponse])
def get_inventory_logs(
    item_id: int = Query(default=None, description="특정 품목 ID의 이력만 필터링할 경우 입력"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "MANAGER"])),
):
    query = db.query(InventoryLog)
    if item_id:
        query = query.filter(InventoryLog.item_id == item_id)
    return query.order_by(InventoryLog.id.desc()).all()