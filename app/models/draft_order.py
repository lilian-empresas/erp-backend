"""
Modelo SQLite para Pedidos em Rascunho (status: EM_DIGITACAO).
Dados complexos (vendedores, cliente, produtos) são armazenados como JSON.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DraftOrder(Base):
    __tablename__ = "draft_orders"

    id = Column(Integer, primary_key=True, index=True)
    nr_ped = Column(Integer, unique=True, index=True, nullable=False)
    status = Column(String, default='EM_DIGITACAO', index=True)

    # Cabeçalho
    data = Column(String, nullable=True)
    arquiteto = Column(String, nullable=True)
    perc_venda_comiss = Column(Float, default=9.0)

    # Pagamento
    f_pagto = Column(String, nullable=True)
    recebim = Column(String, nullable=True)
    qt_parc = Column(Integer, default=1)
    marketing_perc = Column(Float, default=0)
    tx_desloc = Column(Float, default=0)
    desc_acresc_perc = Column(Float, default=0)

    # Dados complexos como JSON
    vendedores_json = Column(Text, default='[]')
    cliente_json = Column(Text, default='{}')
    produtos_json = Column(Text, default='[]')

    # Totais calculados (cache)
    vlr_total = Column(Float, default=0)

    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
