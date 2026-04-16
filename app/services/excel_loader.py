try:
    import pandas as pd
except ImportError:
    pd = None  # pandas indisponível no servidor compartilhado
import os

# Caminho baseado na localização DESTE arquivo (não do CWD, que varia por ambiente)
# excel_loader.py está em: backend/app/services/excel_loader.py
# Subindo 4 níveis:  services -> app -> backend -> projeto_root
# Projeto root:      ERP_Antigravity/  (local) ou /opt/render/project/src/ (Render)
_THIS_FILE = os.path.abspath(__file__)
_PROJECT_ROOT = os.path.dirname(           # projeto_root
                    os.path.dirname(       # backend/
                        os.path.dirname(   # backend/app/
                            os.path.dirname(_THIS_FILE)  # backend/app/services/
                        )
                    )
                )

FILE_PATH = os.path.join(_PROJECT_ROOT, 'data', 'entrada', 'Tabelas.xlsx')
print(f"[excel_loader] Projeto root: {_PROJECT_ROOT}")
print(f"[excel_loader] Arquivo Excel: {FILE_PATH}")
print(f"[excel_loader] Existe: {os.path.exists(FILE_PATH)}")

def load_curtain_data():
    """
    Lê as abas 'Cadastro Cortinas' e 'Valores Cortinas' do arquivo Excel.
    Retorna estrutura JSON pronta para o Frontend.
    """
    if not os.path.exists(FILE_PATH):
        print(f"ERRO: Arquivo não encontrado em {FILE_PATH}")
        return {"error": "Arquivo Tabelas.xlsx não encontrado", "fabrics": [], "prices": []}
    
    try:
        # 1. Ler Tecidos (Fabrics)
        # Colunas esperadas: COD, NOME, LARGURA, Grupo desc, $
        df_fabrics = pd.read_excel(FILE_PATH, sheet_name='Cadastro Cortinas')
        fabrics = []
        for _, row in df_fabrics.iterrows():
            # Tratamento robusto de NaN
            fabrics.append({
                "code": str(row.get('COD', '') if pd.notna(row.get('COD')) else '').strip(),
                "name": str(row.get('NOME', '') if pd.notna(row.get('NOME')) else '').strip(),
                "width": float(row.get('LARGURA', 0) if pd.notna(row.get('LARGURA')) else 0),
                "groupDesc": str(row.get('Grupo desc', '') if pd.notna(row.get('Grupo desc')) else '').strip(),
                "price": float(row.get('$', 0) if pd.notna(row.get('$')) else 0)
            })
            
        # 2. Ler Tabela de Preços (Prices)
        # Colunas esperadas: COD, MODELO, TIPO, GE, G1..G8
        df_prices = pd.read_excel(FILE_PATH, sheet_name='Valores Cortinas')
        prices = []
        for _, row in df_prices.iterrows():
            prices.append({
                "cod": str(row.get('COD', '') if pd.notna(row.get('COD')) else '').strip(),
                "model": str(row.get('MODELO', '') if pd.notna(row.get('MODELO')) else '').strip(),
                "type": str(row.get('TIPO', '') if pd.notna(row.get('TIPO')) else '').strip(),
                # Preços por Grupo
                "GE": float(row.get('GE', 0) if pd.notna(row.get('GE')) else 0),
                "G1": float(row.get('G1', 0) if pd.notna(row.get('G1')) else 0),
                "G2": float(row.get('G2', 0) if pd.notna(row.get('G2')) else 0),
                "G3": float(row.get('G3', 0) if pd.notna(row.get('G3')) else 0),
                "G4": float(row.get('G4', 0) if pd.notna(row.get('G4')) else 0),
                "G5": float(row.get('G5', 0) if pd.notna(row.get('G5')) else 0),
                "G6": float(row.get('G6', 0) if pd.notna(row.get('G6')) else 0),
                "G7": float(row.get('G7', 0) if pd.notna(row.get('G7')) else 0),
                "G8": float(row.get('G8', 0) if pd.notna(row.get('G8')) else 0),
            })
            
        return {"fabrics": fabrics, "prices": prices}
        
    except Exception as e:
        print(f"ERRO ao ler Excel: {e}")
        return {"error": str(e), "fabrics": [], "prices": []}
