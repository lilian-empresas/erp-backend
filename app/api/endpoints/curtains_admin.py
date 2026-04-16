"""
Endpoint administrativo: importa dados de curtinas para o banco.
Uso único no deploy inicial — substitui a leitura do Tabelas.xlsx.

Endpoints:
  POST /api/admin/import-curtains   ← recebe seed_curtains.json no body
  GET  /api/admin/curtains-status   ← verifica se dados já foram importados
"""
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.curtain import CurtainFabric, CurtainPrice

router = APIRouter()


@router.get("/curtains-status")
def curtains_status(db: Session = Depends(get_db)):
    """Verifica quantos registros de curtinas existem no banco."""
    n_fabrics = db.query(CurtainFabric).count()
    n_prices  = db.query(CurtainPrice).count()
    return {
        "fabrics_count": n_fabrics,
        "prices_count":  n_prices,
        "importado":     n_fabrics > 0 or n_prices > 0,
        "status": "✅ Dados importados" if n_fabrics > 0 else "⚠️ Banco vazio — rode a importação"
    }


@router.post("/import-curtains")
async def import_curtains(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa dados de curtinas a partir do seed_curtains.json gerado pelo migrate_excel.py.

    - Aceita apenas arquivos .json
    - Limpa registros anteriores antes de inserir (idempotente)
    - Retorna resumo da importação
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .json gerado pelo migrate_excel.py")

    content = await file.read()
    try:
        seed = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")

    fabrics_data = seed.get("fabrics", [])
    prices_data  = seed.get("prices", [])

    if not fabrics_data and not prices_data:
        raise HTTPException(status_code=400, detail="Arquivo JSON vazio ou sem as chaves 'fabrics' e 'prices'")

    # Limpa dados antigos (idempotente — pode rodar mais de uma vez com segurança)
    deleted_f = db.query(CurtainFabric).delete()
    deleted_p = db.query(CurtainPrice).delete()
    db.commit()

    # Insere tecidos
    inserted_f = 0
    skipped_f  = 0
    for f in fabrics_data:
        code = f.get("code", "").strip()
        if not code:
            skipped_f += 1
            continue
        db.add(CurtainFabric(
            code       = code,
            name       = f.get("name", ""),
            width      = float(f.get("width", 0) or 0),
            group_desc = f.get("group_desc", ""),
            price      = float(f.get("price", 0) or 0),
            active     = True,
        ))
        inserted_f += 1

    # Insere preços
    inserted_p = 0
    skipped_p  = 0
    for p in prices_data:
        cod = p.get("cod", "").strip()
        if not cod:
            skipped_p += 1
            continue
        db.add(CurtainPrice(
            cod   = cod,
            model = p.get("model", ""),
            type  = p.get("type", ""),
            GE = float(p.get("GE", 0) or 0),
            G1 = float(p.get("G1", 0) or 0),
            G2 = float(p.get("G2", 0) or 0),
            G3 = float(p.get("G3", 0) or 0),
            G4 = float(p.get("G4", 0) or 0),
            G5 = float(p.get("G5", 0) or 0),
            G6 = float(p.get("G6", 0) or 0),
            G7 = float(p.get("G7", 0) or 0),
            G8 = float(p.get("G8", 0) or 0),
        ))
        inserted_p += 1

    db.commit()

    return {
        "success": True,
        "fabrics": {"inseridos": inserted_f, "ignorados": skipped_f, "removidos_antes": deleted_f},
        "prices":  {"inseridos": inserted_p, "ignorados": skipped_p, "removidos_antes": deleted_p},
        "mensagem": f"✅ Importação concluída: {inserted_f} tecidos e {inserted_p} preços carregados no banco."
    }
