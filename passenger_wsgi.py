"""
passenger_wsgi.py — Entry point para cPanel Python App (Passenger/WSGI).

Configurações no cPanel > Setup Python App:
  Python version:          3.11.12
  Application root:        erp_api          ← pasta exclusiva da API
  Application URL:         api.summerconceito.com.br  ← subdomínio só da API
  Application entry file:  passenger_wsgi.py
  Application startup file: passenger_wsgi.py
  Entry point:             application

IMPORTANTE:
  O frontend React fica em intra.summerconceito.com.br (pasta pública normal).
  A API fica em api.summerconceito.com.br (Python App separado).
  Assim o deploy do frontend não interfere nos arquivos .htaccess da API.
"""
import sys
import os

# Adiciona a raiz do app ao path do Python
app_root = os.path.dirname(os.path.abspath(__file__))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

# Carrega variáveis do .env se existir
try:
    from dotenv import load_dotenv
    env_path = os.path.join(app_root, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[passenger_wsgi] .env carregado de: {env_path}")
except Exception as e:
    print(f"[passenger_wsgi] Aviso: dotenv não disponível ({e})")

# Variáveis de ambiente padrão para produção (se não definidas via cPanel)
os.environ.setdefault("DATABASE_URL",      "sqlite:///./erp.db")
os.environ.setdefault("PYTHON_ENV",        "production")

# Importa o app FastAPI (ASGI) e o adapta para WSGI (Passenger)
try:
    from app.main import app as fastapi_app
except Exception as e:
    print(f"[passenger_wsgi] ERRO ao importar app: {e}")
    raise

# Passenger exige um callable WSGI chamado 'application'
# FastAPI é ASGI — usamos asgiref para adaptar
try:
    from asgiref.wsgi import WsgiToAsgi  # noqa — não existe, é o contrário
    # Correction: para ASGI→WSGI, usamos a2wsgi
    raise ImportError("use a2wsgi")
except ImportError:
    pass

try:
    from a2wsgi import ASGIMiddleware
    application = ASGIMiddleware(fastapi_app)
    print("[passenger_wsgi] ✅ Usando a2wsgi (ASGIMiddleware)")
except ImportError:
    # Fallback: uvicorn pode ser usado como servidor ASGI diretamente
    # O Passenger suporta ASGI via .htaccess com PassengerAppType wsgi
    # Neste caso, o próprio uvicorn gerencia — passenger_wsgi.py não é usado
    print("[passenger_wsgi] ⚠️ a2wsgi não encontrado — certifique-se de instalar: pip install a2wsgi")
    raise ImportError(
        "Instale a2wsgi: pip install a2wsgi\n"
        "Ou configure o Passenger para rodar como ASGI via uvicorn."
    )
