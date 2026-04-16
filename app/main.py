from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from app.core import config
from app.core.config import settings
from app.core.database import engine, Base
from app.models import config as config_model
from app.models import product as product_model
from app.models import order as order_model
from app.models import draft_order as draft_order_model  # noqa: F401 — registra tabela draft_orders
from app.models import curtain as curtain_model           # noqa: F401 — registra curtain_fabrics e curtain_prices
from app.api.endpoints import products

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="ERP Antigravity API",
    description="Backend API para o ERP Antigravity (FastAPI + SQLCipher)",
    version="0.1.0",
)

# Includes Routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
from app.api.endpoints import orders, imports, categories, settings as settings_api, industrial_orders, curtains, drafts
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(imports.router, prefix="/api/imports", tags=["imports"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])
app.include_router(industrial_orders.router, prefix="/api/orders/industrial", tags=["industrial_orders"])
app.include_router(drafts.router, prefix="/api/orders/drafts", tags=["drafts"])
app.include_router(curtains.router, prefix="/api/products/cortinas", tags=["cortinas"])

# ── Importação de dados (uso administrativo) ──────────────────────────────
from app.api.endpoints import curtains_admin
app.include_router(curtains_admin.router, prefix="/api/admin", tags=["admin"])

# Configuração de CORS — usa a lista completa de config.py (dev + produção Render.com)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de Arquivos Estáticos (Frontend Build para Modo Portátil)
import sys

# Se estiver rodando pelo PyInstaller (frozen), os arquivos estáticos ficam na pasta temporária (_MEIPASS)
if getattr(sys, 'frozen', False):
    static_path = os.path.join(sys._MEIPASS, "static")
else:
    static_path = "static"

if os.path.exists(static_path):
    print(f"Servindo frontend de: {static_path}")
    # Monta assets
    app.mount("/assets", StaticFiles(directory=f"{static_path}/assets"), name="assets")

    # Rota Catch-All para SPA (React Router)
    # Qualquer rota não capturada pela API retorna o index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Se for rota de API ou Docs que não existe, retorna 404 JSON
        if full_path.startswith("api") or full_path in ["docs", "openapi.json"]:
             return JSONResponse({"detail": "Not Found"}, status_code=404)
        
        # Caso contrário, serve index.html para o React lidar com a rota cliente
        return FileResponse(f"{static_path}/index.html")

else:
    # Modo Desenvolvimento (Backend Only)
    @app.get("/")
    def read_root():
        """Rota raiz de desenvolvimento."""
        return {
            "sistema": "ERP Antigravity (Dev Mode)",
            "status": "online",
            "versao": "0.1.0",
            "obs": "Frontend não encontrado em /static. Execute 'npm run build' e copie 'dist' para 'backend/static' para o modo produção."
        }

@app.get("/api/health")
def health_check():
    """Endpoint para monitoramento de saúde da API."""
    return {"status": "ok", "services": {"database": "unknown"}}

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    
    # Se estiver rodando como executável
    if getattr(sys, 'frozen', False):
        # Abre o navegador automaticamente
        webbrowser.open("http://localhost:8000")
        
        # Roda o servidor (sem reload, aceitando conexões externas se necessário)
        # Importante: Passar 'app' objeto, não string
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, workers=1)
    else:
        # Modo Dev
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
