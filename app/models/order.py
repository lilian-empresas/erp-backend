from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True, nullable=True) # Cliente opcional por enquanto
    status = Column(String, default=OrderStatus.PENDING)
    total_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento 1:N com Itens
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, customer='{self.customer_name}', total={self.total_amount})>"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Snapshot dos dados do produto no momento da venda (importante!)
    product_sku = Column(String) 
    product_name = Column(String)
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relacionamentos
    order = relationship("Order", back_populates="items")
    product = relationship("app.models.product.Product")

    def __repr__(self):
        return f"<OrderItem(sku='{self.product_sku}', qty={self.quantity})>"
