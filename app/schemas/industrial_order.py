from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class VendedorItem(BaseModel):
    """Representa um vendedor e seu percentual de comissão"""
    vendedor: str = Field(..., description="Nome do vendedor")
    percentual: float = Field(..., ge=0, le=100, description="Percentual de comissão (0-100)")

class ClienteData(BaseModel):
    """Dados completos do cliente para a aba VENDAS_CLIENTES"""
    cliente: str = Field(..., description="Nome do cliente")
    cpf: Optional[str] = Field(None, description="CPF do cliente")
    end_entrega: str = Field(..., description="Endereço de entrega")
    bairro: Optional[str] = None
    cidade_uf: Optional[str] = None
    cep: Optional[str] = None
    fones: Optional[str] = Field(None, description="Telefones do cliente")
    aniversario: Optional[str] = Field(None, description="Data de aniversário")
    obs: Optional[str] = Field(None, description="Observações gerais")

class ProdutoItem(BaseModel):
    """Item de produto para a aba PRODUTOS"""
    qt: int = Field(..., gt=0, description="Quantidade")
    produto: str = Field(..., description="Nome/código do produto")
    vlr_unit_av: float = Field(..., ge=0, description="Valor unitário à vista")
    vlr_unit_real: Optional[float] = Field(None, description="Valor unitário real")
    categoria: str = Field(..., description="Categoria do produto (CORTINAS, SIERRA, etc)")
    especificacoes: Optional[str] = Field(None, description="Especificações técnicas")
    local_instalacao: Optional[str] = Field(None, description="Local de instalação")
    obs: Optional[str] = None
    garantia: Optional[str] = None

class IndustrialOrderCreate(BaseModel):
    """Schema para criação de pedido industrial completo"""
    
    # Nr_Ped é digitado pelo usuário (não auto-gerado)
    nr_ped: int = Field(..., description="Número do pedido (digitado pelo usuário)")
    
    # Dados do pedido
    data: str = Field(..., description="Data do pedido (YYYY-MM-DD)")
    arquiteto: Optional[str] = Field(None, description="Nome do arquiteto/designer")
    perc_venda_comiss: float = Field(..., ge=0, le=100, description="Percentual de venda comissionada")
    
    # Forma de pagamento
    f_pagto: str = Field(..., description="Forma de pagamento")
    recebim: Optional[str] = Field(None, description="Forma de recebimento (Na Entrega / Após)")
    qt_parc: int = Field(1, ge=1, le=12, description="Quantidade de parcelas")
    
    # Valores adicionais
    marketing_perc: Optional[float] = Field(0, ge=0, description="Percentual de marketing")
    tx_desloc: Optional[float] = Field(0, ge=0, description="Taxa de deslocamento")
    desc_acresc_perc: Optional[float] = Field(None, description="Desconto/Acréscimo percentual")
    
    # Vendedores (mínimo 1, máximo 3)
    vendedores: List[VendedorItem] = Field(..., min_items=1, max_items=3)
    
    # Cliente
    cliente: ClienteData
    
    # Produtos (mínimo 1 item)
    produtos: List[ProdutoItem] = Field(..., min_items=1)

class IndustrialOrderResponse(BaseModel):
    """Resposta após criação de pedido"""
    nr_ped: int
    status: str = "success"
    message: str = "Pedido salvo com sucesso"
