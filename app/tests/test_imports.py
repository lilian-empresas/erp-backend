# ============================================================================
# TESTE DE VALIDAÇÃO - IMPORTAÇÕES PYTHON
# ============================================================================
# Este arquivo testa se todas as dependências Python foram instaladas corretamente
# Execute: python backend/app/tests/test_imports.py
# ============================================================================

import sys
from typing import List, Tuple

def get_version(module):
    """Safely get version string from module."""
    return getattr(module, "__version__", getattr(module, "Version", getattr(module, "version", "Unknown")))

def test_imports() -> List[Tuple[str, bool, str]]:
    """
    Testa importação de todas as dependências críticas.
    
    Returns:
        Lista de tuplas (nome_lib, sucesso, mensagem_erro)
    """
    results = []
    
    # ──────────────────────────────────────────────────────────────────────
    # Framework Web
    # ──────────────────────────────────────────────────────────────────────
    try:
        import fastapi
        results.append(("FastAPI", True, get_version(fastapi)))
    except ImportError as e:
        results.append(("FastAPI", False, str(e)))
    
    try:
        import uvicorn
        results.append(("Uvicorn", True, get_version(uvicorn)))
    except ImportError as e:
        results.append(("Uvicorn", False, str(e)))
    
    # ──────────────────────────────────────────────────────────────────────
    # Banco de Dados
    # ──────────────────────────────────────────────────────────────────────
    try:
        import sqlalchemy
        results.append(("SQLAlchemy", True, get_version(sqlalchemy)))
    except ImportError as e:
        results.append(("SQLAlchemy", False, str(e)))
    
    try:
        from pysqlcipher3 import dbapi2 as sqlite
        results.append(("SQLCipher", True, "OK"))
    except ImportError:
        try:
            import sqlite3
            results.append(("SQLite3 (No Encryption)", True, get_version(sqlite3) + " (DEV ONLY)"))
        except ImportError as e:
            results.append(("SQLCipher", False, str(e)))
    
    # ──────────────────────────────────────────────────────────────────────
    # Segurança
    # ──────────────────────────────────────────────────────────────────────
    try:
        import jose
        results.append(("Python-JOSE", True, "OK"))
    except ImportError as e:
        results.append(("Python-JOSE", False, str(e)))
    
    try:
        import passlib
        results.append(("Passlib", True, get_version(passlib)))
    except ImportError as e:
        results.append(("Passlib", False, str(e)))
    
    try:
        import bcrypt
        results.append(("Bcrypt", True, get_version(bcrypt)))
    except ImportError as e:
        results.append(("Bcrypt", False, str(e)))
    
    # ──────────────────────────────────────────────────────────────────────
    # Arquivos CSV/Excel
    # ──────────────────────────────────────────────────────────────────────
    try:
        import pandas
        results.append(("Pandas", True, get_version(pandas)))
    except ImportError as e:
        results.append(("Pandas", False, str(e)))
    
    try:
        import openpyxl
        results.append(("OpenPyXL", True, get_version(openpyxl)))
    except ImportError as e:
        results.append(("OpenPyXL", False, str(e)))
    
    # ──────────────────────────────────────────────────────────────────────
    # PDF
    # ──────────────────────────────────────────────────────────────────────
    try:
        import reportlab
        results.append(("ReportLab", True, get_version(reportlab)))
    except ImportError as e:
        results.append(("ReportLab", False, str(e)))
    
    try:
        import barcode
        results.append(("Python-Barcode", True, get_version(barcode)))
    except ImportError as e:
        results.append(("Python-Barcode", False, str(e)))
    
    try:
        import qrcode
        results.append(("QRCode", True, get_version(qrcode)))
    except ImportError as e:
        results.append(("QRCode", False, str(e)))
    
    # ──────────────────────────────────────────────────────────────────────
    # Utilidades
    # ──────────────────────────────────────────────────────────────────────
    try:
        import pydantic
        results.append(("Pydantic", True, get_version(pydantic)))
    except ImportError as e:
        results.append(("Pydantic", False, str(e)))
    
    try:
        import dotenv
        results.append(("Python-Dotenv", True, "OK"))
    except ImportError as e:
        results.append(("Python-Dotenv", False, str(e)))
    
    try:
        import loguru
        results.append(("Loguru", True, "OK"))
    except ImportError as e:
        results.append(("Loguru", False, str(e)))
    
    # ──────────────────────────────────────────────────────────────────────
    # Testes
    # ──────────────────────────────────────────────────────────────────────
    try:
        import pytest
        results.append(("Pytest", True, get_version(pytest)))
    except ImportError as e:
        results.append(("Pytest", False, str(e)))
    
    try:
        import httpx
        results.append(("HTTPX", True, get_version(httpx)))
    except ImportError as e:
        results.append(("HTTPX", False, str(e)))
    
    return results


if __name__ == "__main__":
    print("=" * 80)
    print(" TESTE DE VALIDAÇÃO - DEPENDÊNCIAS PYTHON")
    print("=" * 80)
    print()
    
    results = test_imports()
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for lib_name, success, msg in results:
        status = "[OK]  " if success else "[ERRO]"
        print(f"{status:8} | {lib_name:20} | {msg}")
    
    print()
    print("=" * 80)
    print(f" RESULTADO: {success_count}/{total_count} dependências instaladas corretamente")
    print("=" * 80)
    
    if success_count == total_count:
        print("\n[SUCESSO] TODAS AS DEPENDÊNCIAS ESTÃO FUNCIONANDO!")
        sys.exit(0)
    else:
        print(f"\n[FALHA] {total_count - success_count} DEPENDÊNCIAS COM PROBLEMA")
        print("\nExecute: pip install -r requirements.txt")
        sys.exit(1)
