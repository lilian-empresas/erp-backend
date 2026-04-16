from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from app.core.config import settings
import os

# ─────────────────────────────────────────────────────────────────────────────
# [HISTÓRICO - 10/03/2026] Suporte Dual: SQLite (dev local) + PostgreSQL (prod)
#
# Desenvolvimento local (.env com DATABASE_URL sqlite):
#   → SQLite roda como arquivo local, zero configuração extra
#   → check_same_thread=False necessário para FastAPI (múltiplas threads)
#
# Produção Render.com (env var DATABASE_URL postgresql://...):
#   → PostgreSQL via psycopg2-binary
#   → pool_pre_ping=True: verifica conexão antes de usar (reconecta se cair)
#   → pool_size e max_overflow: gerencia conexões simultâneas eficientemente
#   → NÃO usa check_same_thread (exclusivo do SQLite)
#
# A troca é automática — detectada pela string de conexão.
# Nenhum endpoint ou model precisou ser alterado. SQLAlchemy ORM abstrai tudo.
# ─────────────────────────────────────────────────────────────────────────────

_is_sqlite = "sqlite" in settings.DATABASE_URL
_is_postgres = "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL

# Garantir que o diretório existe quando usando SQLite localmente
if _is_sqlite:
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and db_dir != ".":
        os.makedirs(db_dir, exist_ok=True)

# URL de conexão
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Render.com (e alguns provedores) retornam URL com prefixo "postgres://"
# mas o SQLAlchemy 2.x exige "postgresql://". Corrige automaticamente:
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuração do Engine — args variam por banco
if _is_sqlite:
    # SQLite: check_same_thread=False necessário para uso com FastAPI
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL (produção): pool de conexões para suportar múltiplos usuários
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,    # reconecta automaticamente se conexão cair
        pool_size=5,           # conexões simultâneas mantidas abertas
        max_overflow=10,       # conexões extras permitidas em pico de uso
    )

# Sessão Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os Models
Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency para obter sessão do banco de dados em endpoints.
    Garante que a conexão seja fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
