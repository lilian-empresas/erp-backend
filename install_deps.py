"""
install_deps.py — Instala requirements_prod.txt via cPanel "Execute python script".
Uso: campo "Execute python script" no Setup Python App → digitar install_deps.py → Run Script

Estratégia:
  1. Atualiza pip
  2. Tenta instalar requirements_prod.txt com --prefer-binary (sem compilar C)
  3. Se algum falhar, tenta individualmente com fallbacks
"""
import subprocess
import sys
import os

PIP = [sys.executable, "-m", "pip"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQ_FILE = os.path.join(BASE_DIR, "requirements_prod.txt")

def run(args, label=""):
    tag = label or " ".join(args[-2:])
    print(f"\n  >> {tag}", flush=True)
    r = subprocess.run(args, capture_output=True, text=True)
    output = (r.stdout + r.stderr).strip()
    # Mostra últimas linhas relevantes
    lines = [l for l in output.split("\n") if l.strip() and "[notice]" not in l]
    for line in lines[-6:]:
        print(f"     {line}", flush=True)
    return r.returncode

print("=" * 60, flush=True)
print("ERP Antigravity — Instalação de Dependências", flush=True)
print(f"Python: {sys.version}", flush=True)
print(f"Pip:    {sys.executable}", flush=True)
print("=" * 60, flush=True)

# Passo 1: Atualizar pip
print("\n[1/3] Atualizando pip...", flush=True)
run(PIP + ["install", "--upgrade", "pip"], "upgrade pip")

# Passo 2: Instalar tudo de uma vez com --prefer-binary
print(f"\n[2/3] Instalando {REQ_FILE} com --prefer-binary...", flush=True)
rc = run(
    PIP + ["install", "--prefer-binary", "-r", REQ_FILE],
    "pip install --prefer-binary -r requirements_prod.txt"
)

if rc == 0:
    print("\n✅ Todos os pacotes instalados com sucesso!", flush=True)
else:
    # Passo 3: Fallback — instala pacote por pacote
    print("\n[3/3] Algumas falhas — tentando individualmente...", flush=True)
    failed = []

    with open(REQ_FILE) as f:
        pkgs = [
            l.strip() for l in f
            if l.strip() and not l.startswith("#")
        ]

    for pkg in pkgs:
        print(f"\n  -> {pkg}", flush=True)
        # Tenta binário primeiro
        rc1 = run(PIP + ["install", "--prefer-binary", pkg], pkg)
        if rc1 != 0:
            # Tenta sem pinning de versão
            pkg_name = pkg.split("==")[0].split(">=")[0].split("[")[0]
            rc2 = run(PIP + ["install", "--prefer-binary", pkg_name], f"{pkg_name} (sem versão)")
            if rc2 != 0:
                failed.append(pkg)

    print("\n" + "=" * 60, flush=True)
    if failed:
        print(f"❌ FALHOU ({len(failed)} pacotes):", flush=True)
        for p in failed:
            print(f"   - {p}", flush=True)
    else:
        print("✅ Todos instalados com sucesso (modo individual)!", flush=True)
    print("=" * 60, flush=True)

# Verificação final dos pacotes críticos
print("\n[VERIFICAÇÃO] Importando módulos críticos...", flush=True)
criticos = [
    ("fastapi", "FastAPI"),
    ("sqlalchemy", "SQLAlchemy"),
    ("pydantic", "Pydantic"),
    ("a2wsgi", "a2wsgi (WSGI adapter)"),
    ("dotenv", "python-dotenv"),
    ("pandas", "Pandas"),
    ("reportlab", "ReportLab"),
]

for modulo, nome in criticos:
    try:
        m = __import__(modulo)
        v = getattr(m, "__version__", "?")
        print(f"  ✅ {nome} v{v}", flush=True)
    except ImportError as e:
        print(f"  ❌ {nome} — FALHOU: {e}", flush=True)

print("\nFim.", flush=True)
