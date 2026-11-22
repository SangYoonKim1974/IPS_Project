from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AssetInventory(Base):
    __tablename__ = "assets_inventory"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String(20), nullable=False)  # CONSUMABLE(소모품), ASSET(고정자산)
    item_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=5)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="AVAILABLE")  # AVAILABLE, IN_USE, BROKEN, DISPOSED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    logs = relationship("InventoryLog", back_populates="item")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("assets_inventory.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(20), nullable=False)  # IN, OUT, ASSIGN, RETURN
    change_amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("AssetInventory", back_populates="logs")