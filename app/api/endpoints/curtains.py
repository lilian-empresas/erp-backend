"""
Endpoint de dados de Cortinas — lê do banco de dados (SQLite/PostgreSQL).

[Migração 13/04/2026] Substituiu leitura do Tabelas.xlsx por consulta direta
ao banco. Estrutura de resposta mantida idêntica para compatibilidade com frontend.
Dados são populados via POST /api/admin/import-curtains (seed_curtains.json).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.curtain import CurtainFabric, CurtainPrice

router = APIRouter()


@router.get("/tables")
def read_curtain_tables(db: Session = Depends(get_db)):
    """
    Retorna os dados completos das tabelas de Cortinas (Tecidos e Preços).
    Usado pelo Frontend para popular selects e realizar cálculos offline.
    Dados lidos do banco de dados (substitui leitura do Tabelas.xlsx).
    """
    fabrics_db = db.query(CurtainFabric).filter(CurtainFabric.active == True).all()
    prices_db  = db.query(CurtainPrice).all()

    if not fabrics_db and not prices_db:
        return {
            "warning": "Banco de dados de curtinas vazio. Execute POST /api/admin/import-curtains para importar os dados.",
            "fabrics": [],
            "prices":  []
        }

    fabrics = [
        {
            "code":      f.code,
            "name":      f.name,
            "width":     f.width,
            "groupDesc": f.group_desc,  # mantém camelCase do frontend
            "price":     f.price,
        }
        for f in fabrics_db
    ]

    prices = [
        {
            "cod":   p.cod,
            "model": p.model,
            "type":  p.type,
            "GE": p.GE, "G1": p.G1, "G2": p.G2, "G3": p.G3,
            "G4": p.G4, "G5": p.G5, "G6": p.G6, "G7": p.G7, "G8": p.G8,
        }
        for p in prices_db
    ]

    return {"fabrics": fabrics, "prices": prices}
