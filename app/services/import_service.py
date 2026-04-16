try:
    import pandas as pd
except ImportError:
    pd = None  # pandas indisponível no servidor compartilhado
from sqlalchemy.orm import Session
from app.models.product import Product
from io import BytesIO
from typing import Dict, List, Any

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    async def import_products_from_excel(self, file_content: bytes) -> Dict[str, Any]:
        """
        Importa produtos a partir de um arquivo Excel (.xlsx) ou CSV.
        """
        try:
            # Tentar ler como Excel, se falhar tenta como CSV
            try:
                df = pd.read_excel(BytesIO(file_content))
            except:
                df = pd.read_csv(BytesIO(file_content))

            # Limpar nomes de colunas (remover espaços, lower case)
            df.columns = [str(c).strip().lower() for c in df.columns]

            # Mapeamento esperado: 'sku', 'nome', 'preco', 'estoque', 'categoria'
            # Mapear sinônimos comuns
            mapping = {
                'sku': 'sku',
                'código': 'sku',
                'codigo': 'sku',
                'nome': 'name',
                'produto': 'name',
                'preço': 'price',
                'preco': 'price',
                'valor': 'price',
                'estoque': 'stock_quantity',
                'quantidade': 'stock_quantity',
                'categoria': 'category'
            }

            results = {
                "total": len(df),
                "imported": 0,
                "updated": 0,
                "errors": []
            }

            for index, row in df.iterrows():
                try:
                    product_data = {}
                    for col_name, model_field in mapping.items():
                        if col_name in df.columns:
                            product_data[model_field] = row[col_name]

                    if 'sku' not in product_data or pd.isna(product_data['sku']):
                        results["errors"].append(f"Linha {index+2}: SKU não encontrado")
                        continue

                    sku = str(product_data['sku'])
                    
                    # Verificar se já existe
                    db_product = self.db.query(Product).filter(Product.sku == sku).first()

                    if db_product:
                        # Atualizar
                        for key, value in product_data.items():
                            if not pd.isna(value):
                                setattr(db_product, key, value)
                        results["updated"] += 1
                    else:
                        # Criar novo
                        new_product = Product(
                            sku=sku,
                            name=str(product_data.get('name', 'Produto sem nome')),
                            price=float(product_data.get('price', 0.0)),
                            stock_quantity=int(product_data.get('stock_quantity', 0)),
                            category=str(product_data.get('category', 'Geral')) if not pd.isna(product_data.get('category')) else "Geral"
                        )
                        self.db.add(new_product)
                        results["imported"] += 1

                except Exception as e:
                    results["errors"].append(f"Linha {index+2}: {str(e)}")

            self.db.commit()
            return results

        except Exception as e:
            return {"error": f"Falha ao processar arquivo: {str(e)}"}
