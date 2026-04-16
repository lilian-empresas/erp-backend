from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Valores financeiros (armazenando como Float para SQLite simples por enquanto)
    price = Column(Float, default=0.0)
    cost_price = Column(Float, default=0.0)
    
    # Controle de Estoque
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)  # Para alertas de estoque baixo
    
    category = Column(String, index=True, nullable=True)
    barcode = Column(String, unique=True, index=True, nullable=True)
    
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}')>"
