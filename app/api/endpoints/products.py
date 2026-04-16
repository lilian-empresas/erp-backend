from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate, 
    service: ProductService = Depends(get_service)
):
    """
    Criar um novo produto.
    """
    if service.get_product_by_sku(product.sku):
        raise HTTPException(status_code=400, detail="SKU já cadastrado.")
    
    return service.create_product(product)

@router.get("/", response_model=List[Product])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False,
    service: ProductService = Depends(get_service)
):
    """
    Listar produtos com paginação simples.
    """
    return service.get_products(skip=skip, limit=limit, active_only=active_only)

@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int, 
    service: ProductService = Depends(get_service)
):
    """
    Obter detalhes de um produto pelo ID.
    """
    db_product = service.get_product(product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    service: ProductService = Depends(get_service)
):
    """
    Atualizar um produto existente.
    """
    db_product = service.update_product(product_id, product_update)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int, 
    service: ProductService = Depends(get_service)
):
    """
    Remover um produto.
    """
    success = service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return None
