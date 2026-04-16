from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.file_service import FileService
from app.core.config import settings
from app.schemas.industrial_order import IndustrialOrderCreate, IndustrialOrderResponse

router = APIRouter()

@router.post("/", response_model=IndustrialOrderResponse)
async def create_industrial_order(
    order: IndustrialOrderCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo pedido industrial completo.
    Persiste os dados nas 4 abas do arquivo Excel de saída.
    """
    try:
        # Calcular totais
        vlr_av = sum(p.qt * p.vlr_unit_av for p in order.produtos)
        comissao = vlr_av * (order.perc_venda_comiss / 100)
        marketing_rs = vlr_av * ((order.marketing_perc or 0) / 100)
        
        # Montar estrutura de dados para o FileService
        order_data = {
            'nr_ped': order.nr_ped,
            'data': order.data,
            'arquiteto': order.arquiteto,
            'perc_venda_comiss': order.perc_venda_comiss,
            'f_pagto': order.f_pagto,
            'recebim': order.recebim,
            'qt_parc': order.qt_parc,
            'marketing_perc': order.marketing_perc,
            'tx_desloc': order.tx_desloc,
            'desc_acresc_perc': order.desc_acresc_perc,
            
            # Valores calculados
            'vlr_av': vlr_av,
            'vlr_liquido': vlr_av,  # Simplificado por enquanto
            'comissao': comissao,
            'marketing_rs': marketing_rs,
            'vlr_real': None,
            'desc_acresc_rs': None,
            
            # Vendedores
            'vendedores': [v.dict() for v in order.vendedores],
            
            # Cliente
            'cliente': order.cliente.dict(),
            
            # Produtos
            'produtos': [p.dict() for p in order.produtos]
        }
        
        # Usar FileService com paths corretos dos settings (agora absolutos)
        file_service = FileService()
        # FileService já usa settings.DATA_OUTPUT_PATH que agora está correto
        
        result = file_service.append_order_to_excel(order_data)
        
        return IndustrialOrderResponse(
            nr_ped=result['nr_ped'],
            status="success",
            message=f"Pedido {result['nr_ped']} salvo com sucesso no Excel"
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar pedido: {str(e)}")
