from sqlalchemy.orm import Session
from app.models.config import SystemConfig
from app.core.config import settings
import os

class ConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get_config(self, key: str, default: str) -> str:
        config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return config.value if config else default

    def set_config(self, key: str, value: str):
        config = self.db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = value
        else:
            config = SystemConfig(key=key, value=value)
            self.db.add(config)
        self.db.commit()

    def get_app_paths(self):
        """Retorna os caminhos de entrada e saída configurados"""
        return {
            "input_path": self.get_config("folder_produtos", settings.DATA_INPUT_PATH),
            "output_path": self.get_config("folder_vendas", settings.DATA_OUTPUT_PATH)
        }
