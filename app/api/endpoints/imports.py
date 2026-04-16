from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.import_service import ImportService
from typing import Any

router = APIRouter()

@router.post("/products")
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Endpoint para upload de planilha Excel/CSV de produtos.
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Use .xlsx ou .csv")

    content = await file.read()
    service = ImportService(db)
    result = await service.import_products_from_excel(content)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result
