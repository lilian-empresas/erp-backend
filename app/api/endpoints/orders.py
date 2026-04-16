from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.order import Order, OrderCreate
from app.services.order_service import OrderService

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate, 
    service: OrderService = Depends(get_service)
):
    """
    Criar um novo pedido com itens.
    O sistema calculará automaticamente os preços e totais com base nos produtos.
    """
    return service.create_order(order)

@router.get("/", response_model=List[Order])
def read_orders(
    skip: int = 0, 
    limit: int = 100, 
    service: OrderService = Depends(get_service)
):
    """
    Listar pedidos realizados.
    """
    return service.get_orders(skip=skip, limit=limit)

@router.get("/{order_id}", response_model=Order)
def read_order(
    order_id: int, 
    service: OrderService = Depends(get_service)
):
    """
    Obter detalhes completos de um pedido (incluindo itens).
    """
    db_order = service.get_order(order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_order
