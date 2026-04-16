from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_products(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Product]:
        query = self.db.query(Product)
        if active_only:
            query = query.filter(Product.active == True)
        return query.offset(skip).limit(limit).all()

    def create_product(self, product: ProductCreate) -> Product:
        db_product = Product(
            sku=product.sku,
            name=product.name,
            description=product.description,
            price=product.price,
            cost_price=product.cost_price,
            stock_quantity=product.stock_quantity,
            min_stock_level=product.min_stock_level,
            category=product.category,
            barcode=product.barcode,
            active=product.active
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update_product(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        db_product = self.get_product(product_id)
        if not db_product:
            return None
        
        update_data = product_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> bool:
        db_product = self.get_product(product_id)
        if not db_product:
            return False
        
        self.db.delete(db_product)
        self.db.commit()
        return True
