from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings as app_settings
from app.services.config_service import ConfigService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class SettingsSchema(BaseModel):
    # [11/03/2026] folder_vendas removido — dados agora no banco PostgreSQL/SQLite
    # folder_produtos é opcional — pré-configurado no servidor, usuário só altera se necessário
    folder_produtos: Optional[str] = None
    logo_base64: Optional[str] = None

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    service = ConfigService(db)
    logo_base64 = service.get_config("logo_base64", "")
    # Retorna o caminho configurado (do servidor ou salvo pelo usuário)
    folder_produtos = service.get_config("folder_produtos", app_settings.DATA_INPUT_PATH)
    return {
        "input_path": folder_produtos,
        "output_path": "",   # mantido para compatibilidade, mas não é mais usado
        "logo_base64": logo_base64
    }

@router.post("")
def update_settings(data: SettingsSchema, db: Session = Depends(get_db)):
    service = ConfigService(db)
    # Só salva folder_produtos se foi enviado (não sobrescreve o padrão se não enviado)
    if data.folder_produtos is not None:
        service.set_config("folder_produtos", data.folder_produtos)
    if data.logo_base64 is not None:
        service.set_config("logo_base64", data.logo_base64)
    return {"status": "success", "message": "Configurações salvas!"}
