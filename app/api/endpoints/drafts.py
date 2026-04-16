"""
Endpoints para gerenciar Pedidos Rascunho (DraftOrders) e busca de cliente por CPF.
"""
import json
import os
import csv as csv_module
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.draft_order import DraftOrder
from app.schemas.draft_order import (
    DraftOrderCreate, DraftOrderResponse,
    DraftOrderSummary, ClienteBuscaResponse
)
from app.core.config import settings

router = APIRouter()


# ──────────────────────────────────────────────────────────
#  UTILITÁRIOS
# ──────────────────────────────────────────────────────────

def _get_output_file() -> str:
    """Retorna o caminho do arquivo Dados PED.xlsx de saída."""
    return os.path.join(settings.DATA_OUTPUT_PATH, "Dados PED.xlsx")


def _draft_to_summary(draft: DraftOrder) -> DraftOrderSummary:
    """Converte um DraftOrder do banco em DraftOrderSummary."""
    cliente_data = {}
    vendedores_data = []
    try:
        cliente_data = json.loads(draft.cliente_json or '{}')
    except Exception:
        pass
    try:
        vendedores_data = json.loads(draft.vendedores_json or '[]')
    except Exception:
        pass

    cliente_nome = cliente_data.get('cliente') or None
    vendedor_nome = vendedores_data[0].get('vendedor') if vendedores_data else None
    todos_vendedores = [v.get('vendedor') for v in vendedores_data if v.get('vendedor')]

    categorias = {}
    try:
        produtos_data = json.loads(draft.produtos_json or '[]')
        for prod in produtos_data:
            # Normaliza para maiúsculo para garantir consistência no Dashboard
            cat_raw = prod.get('categoria') or 'Sem Categoria'
            cat = cat_raw.strip().upper()
            vlr = prod.get('vlr_unit_av', 0) * prod.get('qt', 1)
            categorias[cat] = categorias.get(cat, 0) + vlr
    except Exception:
        pass

    return DraftOrderSummary(
        id=draft.id,
        nr_ped=draft.nr_ped,
        status=draft.status,
        data=draft.data,
        cliente=cliente_nome,
        vendedor=vendedor_nome,
        todos_vendedores=todos_vendedores,
        arquiteto=draft.arquiteto or None,
        vlr_total=draft.vlr_total or 0,
        categorias=categorias,
        updated_at=draft.updated_at,
    )


def _draft_to_response(draft: DraftOrder) -> DraftOrderResponse:
    """Converte DraftOrder do banco em resposta completa."""
    try:
        vendedores = json.loads(draft.vendedores_json or '[]')
    except Exception:
        vendedores = []
    try:
        cliente = json.loads(draft.cliente_json or '{}')
    except Exception:
        cliente = {}
    try:
        produtos = json.loads(draft.produtos_json or '[]')
    except Exception:
        produtos = []

    return DraftOrderResponse(
        id=draft.id,
        nr_ped=draft.nr_ped,
        status=draft.status,
        data=draft.data,
        arquiteto=draft.arquiteto,
        perc_venda_comiss=draft.perc_venda_comiss,
        f_pagto=draft.f_pagto,
        recebim=draft.recebim,
        qt_parc=draft.qt_parc,
        marketing_perc=draft.marketing_perc,
        tx_desloc=draft.tx_desloc,
        desc_acresc_perc=draft.desc_acresc_perc,
        vendedores=vendedores,
        cliente=cliente or None,
        produtos=produtos,
        vlr_total=draft.vlr_total or 0,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


# ──────────────────────────────────────────────────────────
#  ENDPOINTS — RASCUNHOS
# ──────────────────────────────────────────────────────────

@router.post("/", response_model=DraftOrderResponse)
def salvar_rascunho(payload: DraftOrderCreate, db: Session = Depends(get_db)):
    """
    Cria ou atualiza um pedido em rascunho (EM_DIGITACAO) ou LANCADO no SQLite.
    Se já existir um draft com o mesmo nr_ped, e a flag payload.is_edit for True, ele atualiza.
    Caso contrário, levanta um erro impedindo sobrescrever o pedido sem intenção.
    """
    draft = db.query(DraftOrder).filter(DraftOrder.nr_ped == payload.nr_ped).first()

    if draft and not payload.is_edit:
        raise HTTPException(
            status_code=400, 
            detail=f"O número de pedido {payload.nr_ped} já existe no sistema. Escolha outro número para o novo pedido."
        )

    dados = {
        "nr_ped": payload.nr_ped,
        "status": payload.status or "EM_DIGITACAO",
        "data": payload.data,
        "arquiteto": payload.arquiteto,
        "perc_venda_comiss": payload.perc_venda_comiss,
        "f_pagto": payload.f_pagto,
        "recebim": payload.recebim,
        "qt_parc": payload.qt_parc,
        "marketing_perc": payload.marketing_perc,
        "tx_desloc": payload.tx_desloc,
        "desc_acresc_perc": payload.desc_acresc_perc,
        "vendedores_json": json.dumps(payload.vendedores, ensure_ascii=False),
        "cliente_json": json.dumps(payload.cliente or {}, ensure_ascii=False),
        "produtos_json": json.dumps(payload.produtos, ensure_ascii=False),
        "vlr_total": payload.vlr_total,
    }

    if draft:
        for key, value in dados.items():
            setattr(draft, key, value)
    else:
        draft = DraftOrder(**dados)
        db.add(draft)

    db.commit()
    db.refresh(draft)
    return _draft_to_response(draft)


@router.get("/", response_model=List[DraftOrderSummary])
def listar_rascunhos(
    status: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos os rascunhos de pedido.
    Filtros opcionais: ?status=EM_DIGITACAO ou ?status=LANCADO, data_inicio e data_fim.
    """
    query = db.query(DraftOrder)
    if status:
        query = query.filter(DraftOrder.status == status)
    if data_inicio:
        query = query.filter(DraftOrder.data >= data_inicio)
    if data_fim:
        query = query.filter(DraftOrder.data <= data_fim)
        
    drafts = query.order_by(DraftOrder.updated_at.desc()).all()
    return [_draft_to_summary(d) for d in drafts]


# ──────────────────────────────────────────────────────────
#  ENDPOINT — EXPORTAR DADOS
#  ⚠️ DEVE VIR ANTES DE /{nr_ped}
# ──────────────────────────────────────────────────────────

@router.get("/exportar")
def exportar_pedidos(
    formato: str = "excel",          # "excel" ou "csv"
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    vendedor: Optional[str] = None,
    cliente: Optional[str] = None,
    arquiteto: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Exporta pedidos do banco para Excel ou CSV com filtros opcionais.
    Download imediato via StreamingResponse.
    [13/04/2026] Migrado de pandas para openpyxl direto (servidor sem numpy/pandas).
    """
    from fastapi.responses import StreamingResponse
    import io
    from datetime import datetime

    query = db.query(DraftOrder)

    # Filtros de data sobre a coluna 'data'
    if data_inicio:
        query = query.filter(DraftOrder.data >= data_inicio)
    if data_fim:
        query = query.filter(DraftOrder.data <= data_fim)

    drafts = query.order_by(DraftOrder.data.desc()).all()

    # Cabecalho das colunas
    headers = [
        'Nr. Pedido', 'Data', 'Status', 'Vendedor', 'Cliente', 'CPF',
        'Cidade/UF', 'Arquiteto', 'F. Pagto', 'Qt. Parc.', 'Categoria',
        'Produto', 'Qt', 'Vlr Unit. AV (R$)', 'Total Item (R$)',
        'Local Instalacao', 'Vlr Total Pedido (R$)', 'Comissao %',
        'Tx. Desloc. (R$)', 'Criado em', 'Atualizado em',
    ]

    # Monta linhas
    rows = []
    for d in drafts:
        cliente_data = {}
        vendedores_data = []
        produtos_data = []
        try:
            cliente_data = json.loads(d.cliente_json or '{}')
        except Exception:
            pass
        try:
            vendedores_data = json.loads(d.vendedores_json or '[]')
        except Exception:
            pass
        try:
            produtos_data = json.loads(d.produtos_json or '[]')
        except Exception:
            pass

        vendedor_nome = vendedores_data[0].get('vendedor', '') if vendedores_data else ''
        cliente_nome = cliente_data.get('cliente', '')
        arq = d.arquiteto or cliente_data.get('arquiteto', '')

        # Aplica filtros textuais (case-insensitive)
        if vendedor and vendedor.lower() not in vendedor_nome.lower():
            continue
        if cliente and cliente.lower() not in cliente_nome.lower():
            continue
        if arquiteto and arquiteto.lower() not in arq.lower():
            continue

        def _make_row(prod=None):
            return [
                d.nr_ped,
                d.data,
                d.status,
                vendedor_nome,
                cliente_nome,
                cliente_data.get('cpf', ''),
                cliente_data.get('cidade_uf', ''),
                arq,
                d.f_pagto,
                d.qt_parc,
                prod.get('categoria', '') if prod else '',
                prod.get('produto', '') if prod else '',
                prod.get('qt', 1) if prod else '',
                prod.get('vlr_unit_av', 0) if prod else '',
                round(prod.get('qt', 1) * prod.get('vlr_unit_av', 0), 2) if prod else '',
                prod.get('local_instalacao', '') if prod else '',
                d.vlr_total,
                d.perc_venda_comiss,
                d.tx_desloc,
                d.created_at.strftime('%d/%m/%Y %H:%M') if d.created_at else '',
                d.updated_at.strftime('%d/%m/%Y %H:%M') if d.updated_at else '',
            ]

        if produtos_data:
            for p in produtos_data:
                rows.append(_make_row(p))
        else:
            rows.append(_make_row())

    dt_str = datetime.now().strftime('%Y%m%d_%H%M')

    if formato == 'csv':
        output = io.StringIO()
        writer = csv_module.writer(output, delimiter=';')
        writer.writerow(headers)
        writer.writerows(rows)
        csv_bytes = output.getvalue().encode('utf-8-sig')
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=pedidos_{dt_str}.csv"}
        )
    else:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'Pedidos'
        ws.append(headers)
        for row in rows:
            ws.append(row)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=pedidos_{dt_str}.xlsx"}
        )




# ──────────────────────────────────────────────────────────
#  ENDPOINT — BUSCA CLIENTE POR CPF
#  ⚠️ DEVE VIR ANTES DE /{nr_ped} para não ser capturado como int
# ──────────────────────────────────────────────────────────

@router.get("/buscar-cliente", response_model=ClienteBuscaResponse)
def buscar_cliente_por_cpf(cpf: str, db: Session = Depends(get_db)):
    """
    Busca dados de um cliente pelo CPF nos pedidos salvos no banco de dados.
    [11/03/2026] Migrado de leitura de arquivo Excel local (Dados PED.xlsx)
    para consulta direta ao banco PostgreSQL/SQLite via draft_orders.cliente_json.
    Motivo: deploy em nuvem (Render.com) não possui sistema de arquivos local persistente.
    """
    import json

    cpf_limpo = cpf.replace(".", "").replace("-", "").replace(" ", "").strip()

    if not cpf_limpo:
        raise HTTPException(status_code=400, detail="CPF não pode ser vazio")

    # Busca todos os pedidos (não cancelados), do mais recente ao mais antigo
    pedidos = (
        db.query(DraftOrder)
        .filter(DraftOrder.status != 'CANCELADO')
        .order_by(DraftOrder.nr_ped.desc())
        .all()
    )

    for pedido in pedidos:
        try:
            cliente = json.loads(pedido.cliente_json or '{}')
            cpf_db = str(cliente.get('cpf', '')).replace(".", "").replace("-", "").replace(" ", "").strip()

            if cpf_db == cpf_limpo:
                # Converte aniversário para formato ISO se necessário
                aniversario = cliente.get('aniversario', '') or ''
                if aniversario and '/' in aniversario:
                    import re
                    m = re.match(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})", aniversario)
                    if m:
                        d, mo, y = m.group(1), m.group(2), m.group(3)
                        if len(y) == 2:
                            y = "20" + y
                        aniversario = f"{y}-{mo.zfill(2)}-{d.zfill(2)}"

                return ClienteBuscaResponse(
                    encontrado=True,
                    nr_ped_ref=pedido.nr_ped,
                    cliente=cliente.get('cliente', ''),
                    cpf=cpf,
                    end_entrega=cliente.get('end_entrega', ''),
                    bairro=cliente.get('bairro', ''),
                    cidade_uf=cliente.get('cidade_uf', ''),
                    cep=cliente.get('cep', ''),
                    fones=cliente.get('fones', ''),
                    aniversario=aniversario or None,
                    obs=cliente.get('obs', ''),
                )
        except (json.JSONDecodeError, Exception):
            continue

    return ClienteBuscaResponse(encontrado=False)

# ──────────────────────────────────────────────────────────

#  ENDPOINTS — RASCUNHO POR NR_PED (inteiro)
#  ⚠️ DEVE VIR DEPOIS das rotas com paths fixos!
# ──────────────────────────────────────────────────────────

@router.get("/{nr_ped}", response_model=DraftOrderResponse)
def obter_rascunho(nr_ped: int, db: Session = Depends(get_db)):
    """Retorna um rascunho completo pelo número do pedido."""
    draft = db.query(DraftOrder).filter(DraftOrder.nr_ped == nr_ped).first()
    if not draft:
        raise HTTPException(status_code=404, detail=f"Rascunho do pedido {nr_ped} não encontrado")
    return _draft_to_response(draft)


@router.delete("/{nr_ped}", status_code=204)
def deletar_rascunho(nr_ped: int, db: Session = Depends(get_db)):
    """Deleta um rascunho após lançamento ou cancelamento."""
    draft = db.query(DraftOrder).filter(DraftOrder.nr_ped == nr_ped).first()
    if not draft:
        raise HTTPException(status_code=404, detail=f"Rascunho {nr_ped} não encontrado")
    db.delete(draft)
    db.commit()
