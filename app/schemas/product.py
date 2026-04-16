from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# Base Schema (campos comuns)
class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: float = 0.0
    cost_price: Optional[float] = 0.0
    stock_quantity: int = 0
    min_stock_level: int = 5
    category: Optional[str] = None
    barcode: Optional[str] = None
    active: bool = True

# Schema para Criação (campos obrigatórios adicionais se houver)
class ProductCreate(ProductBase):
    pass

# Schema para Atualização (todos opcionais)
class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    category: Optional[str] = None
    barcode: Optional[str] = None
    active: Optional[bool] = None

# Schema para Leitura (inclui ID e timestamps)
class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Schema para Listagem com Paginação
class ProductList(BaseModel):
    items: List[Product]
    total: int
    page: int
    size: int
