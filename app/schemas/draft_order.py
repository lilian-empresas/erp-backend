"""
Schemas Pydantic para Pedidos Rascunho (DraftOrders).
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class DraftOrderCreate(BaseModel):
    """Schema para criar/atualizar um rascunho de pedido."""
    nr_ped: int = Field(..., description="Número do pedido")
    status: str = Field('EM_DIGITACAO', description="Status")
    is_edit: bool = Field(False, description="Flag que sinaliza se é uma edição de pedido já existente")

    # Cabeçalho
    data: Optional[str] = None
    arquiteto: Optional[str] = None
    perc_venda_comiss: float = 9.0

    # Pagamento
    f_pagto: Optional[str] = None
    recebim: Optional[str] = None
    qt_parc: int = 1
    marketing_perc: float = 0
    tx_desloc: float = 0
    desc_acresc_perc: float = 0

    # Dados complexos
    vendedores: List[Dict[str, Any]] = []
    cliente: Optional[Dict[str, Any]] = None
    produtos: List[Dict[str, Any]] = []

    # Total calculado
    vlr_total: float = 0


class DraftOrderResponse(BaseModel):
    """Schema de resposta ao salvar/recuperar um rascunho."""
    id: int
    nr_ped: int
    status: str
    data: Optional[str]
    arquiteto: Optional[str]
    perc_venda_comiss: float
    f_pagto: Optional[str]
    recebim: Optional[str]
    qt_parc: int
    marketing_perc: float
    tx_desloc: float
    desc_acresc_perc: float
    vendedores: List[Dict[str, Any]] = []
    cliente: Optional[Dict[str, Any]] = None
    produtos: List[Dict[str, Any]] = []
    vlr_total: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DraftOrderSummary(BaseModel):
    """Versão resumida para listagem."""
    id: int
    nr_ped: int
    status: str
    data: Optional[str]
    cliente: Optional[str] = None   # Apenas o nome, extraído do JSON
    vendedor: Optional[str] = None  # Primeiro vendedor, extraído do JSON
    todos_vendedores: Optional[List[str]] = None  # Todos os vendedores do pedido
    arquiteto: Optional[str] = None
    vlr_total: float
    categorias: Optional[Dict[str, float]] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClienteBuscaResponse(BaseModel):
    """Resposta da busca de cliente por CPF."""
    encontrado: bool
    nr_ped_ref: Optional[int] = None    # Nº do pedido mais recente desse cliente
    cliente: Optional[str] = None
    cpf: Optional[str] = None
    end_entrega: Optional[str] = None
    bairro: Optional[str] = None
    cidade_uf: Optional[str] = None
    cep: Optional[str] = None
    fones: Optional[str] = None
    aniversario: Optional[str] = None
    obs: Optional[str] = None
