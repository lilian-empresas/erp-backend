from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate
from typing import List, Optional

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).offset(skip).limit(limit).all()

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def create_order(self, order_in: OrderCreate) -> Order:
        # 1. Criar o objeto Order (cabeçalho)
        db_order = Order(
            customer_name=order_in.customer_name,
            status=OrderStatus.PENDING,
            total_amount=0.0
        )
        self.db.add(db_order)
        self.db.flush() # Gerar o ID do pedido sem commitar ainda

        total_amount = 0.0

        # 2. Processar Itens
        for item_in in order_in.items:
            # Buscar produto para pegar preço e dados
            product = self.db.query(Product).filter(Product.id == item_in.product_id).first()
            
            if not product:
                # Em produção, deveríamos tratar isso melhor (rollback e erro)
                continue
            
            # Calcular valores
            unit_price = product.price
            subtotal = unit_price * item_in.quantity
            
            # Criar Item
            db_item = OrderItem(
                order_id=db_order.id,
                product_id=product.id,
                product_sku=product.sku,
                product_name=product.name,
                quantity=item_in.quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )
            self.db.add(db_item)
            
            total_amount += subtotal

        # 3. Atualizar total do pedido
        db_order.total_amount = total_amount
        
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[Order]:
        order = self.get_order(order_id)
        if not order:
            return None
        
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order
