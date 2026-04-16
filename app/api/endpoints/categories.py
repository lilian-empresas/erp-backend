from fastapi import APIRouter, HTTPException
from app.services.file_service import FileService
from typing import List, Dict, Any

router = APIRouter()
file_service = FileService()

@router.get("/")
def list_categories():
    """
    Lista todas as categorias disponíveis (arquivos na pasta de entrada).
    """
    categories = file_service.get_categories()
    return {"categories": categories}

@router.get("/{category_name}")
def get_category_detail(category_name: str):
    """
    Lê o arquivo da categoria e retorna todas as abas e seus dados.
    """
    data = file_service.read_category_data(category_name)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
