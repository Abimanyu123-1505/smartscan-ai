import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "SmartScan AI"
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: str = os.getenv("DATA_DIR", "/data")

settings = Settings()
