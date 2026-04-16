from pydantic import BaseSettings
from typing import List
import os

# Caminho base do projeto (d:\DEV\ERP_Antigravity)
# config.py está em: backend/app/core/config.py
# Precisamos subir 4 níveis: core -> app -> backend -> ERP_Antigravity
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ERP"

    # ─── CORS ────────────────────────────────────────────────────────────────
    # Em produção, adicione a URL do frontend (Render, HostGator, etc.)
    # via variável de ambiente BACKEND_CORS_ORIGINS no servidor.
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:5173",   # Vite dev server local
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "tauri://localhost",
        # Render.com — fallback (mantido intacto):
        "https://erp-40s9.onrender.com",
        "https://erp-frontend-6izy.onrender.com",
        # Produção summerconceito.com.br:
        "https://intra.summerconceito.com.br",
        "http://intra.summerconceito.com.br",
        # API em subdomínio próprio (api.summerconceito.com.br):
        "https://api.summerconceito.com.br",
        "http://api.summerconceito.com.br",
    ]

    # ─── DATABASE ─────────────────────────────────────────────────────────────
    #
    # [HISTÓRICO - 10/03/2026] Migração SQLite → PostgreSQL
    # Motivo: SQLite é um arquivo local — no Render.com (e nuvem em geral),
    # o sistema de arquivos é efêmero (resetado a cada redeploy/reinício).
    # Isso causaria perda total dos dados a cada atualização de código.
    # O PostgreSQL é um banco de dados servidor independente, com dados
    # persistentes mesmo quando o backend reinicia ou é redeployado.
    # Custo no Render.com Free Tier: R$ 0 (1 GB grátis por 90 dias ativos).
    # O SQLAlchemy ORM abstrai as diferenças — nenhum endpoint precisou mudar.
    #
    # ANTES (SQLite — desenvolvimento local):
    # DATABASE_URL: str = "sqlite:///./backend/erp_antigravity.db"
    #
    # AGORA (PostgreSQL — produção Render.com ou qualquer servidor):
    # A URL vem da variável de ambiente DATABASE_URL definida no servidor.
    # Para desenvolvimento local, crie um arquivo .env na pasta backend/ com:
    #   DATABASE_URL=sqlite:///./backend/erp_antigravity.db
    # Assim o banco local continua funcionando sem alteração.
    DATABASE_URL: str = "sqlite:///./erp_antigravity.db"

    # ─── PATHS DE DADOS ──────────────────────────────────────────────────────
    # Em produção, esses paths apontarão para diretório no servidor
    DATA_INPUT_PATH: str = os.path.join(_BASE_DIR, "data", "entrada")
    DATA_OUTPUT_PATH: str = os.path.join(_BASE_DIR, "data", "saida")

    class Config:
        case_sensitive = True
        env_file = ".env"          # Carrega .env local se existir
        env_file_encoding = "utf-8"

settings = Settings()
