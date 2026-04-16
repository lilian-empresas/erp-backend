"""
Models para dados de Cortinas — substituem as abas Excel:
  • 'Cadastro Cortinas' → CurtainFabric
  • 'Valores Cortinas'  → CurtainPrice

[Migração: 13/04/2026] Dados previamente lidos do Tabelas.xlsx.
Agora persistidos no banco de dados para permitir deploy sem arquivos locais.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class CurtainFabric(Base):
    """
    Tecidos/Cadastro de Cortinas.
    Equivalente à aba 'Cadastro Cortinas' do Tabelas.xlsx.
    Colunas: COD, NOME, LARGURA, Grupo desc, $
    """
    __tablename__ = "curtain_fabrics"

    id         = Column(Integer, primary_key=True, index=True)
    code       = Column(String(50), unique=True, index=True, nullable=False)
    name       = Column(String(200), nullable=False)
    width      = Column(Float, default=0.0)
    group_desc = Column(String(100), nullable=True)
    price      = Column(Float, default=0.0)
    active     = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CurtainFabric(code='{self.code}', name='{self.name}')>"


class CurtainPrice(Base):
    """
    Tabela de Preços de Cortinas.
    Equivalente à aba 'Valores Cortinas' do Tabelas.xlsx.
    Colunas: COD, MODELO, TIPO, GE, G1..G8
    """
    __tablename__ = "curtain_prices"

    id    = Column(Integer, primary_key=True, index=True)
    cod   = Column(String(50), index=True, nullable=False)
    model = Column(String(200), nullable=True)
    type  = Column(String(100), nullable=True)
    # Preços por grupo
    GE = Column(Float, default=0.0)
    G1 = Column(Float, default=0.0)
    G2 = Column(Float, default=0.0)
    G3 = Column(Float, default=0.0)
    G4 = Column(Float, default=0.0)
    G5 = Column(Float, default=0.0)
    G6 = Column(Float, default=0.0)
    G7 = Column(Float, default=0.0)
    G8 = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CurtainPrice(cod='{self.cod}', model='{self.model}')>"
