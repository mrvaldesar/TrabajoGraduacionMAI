import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "API Trabajo de Graduación"
    API_V1_STR: str = "/api/v1"

    # Model Paths
    # Default to local folder structure, can be overridden by env vars
    BETO_MODEL_PATH: str = os.getenv("BETO_MODEL_PATH", "models/modelo_beto_finetuned_v1")
    SBERT_MODEL_PATH: str = os.getenv("SBERT_MODEL_PATH", "models/modelo_sbert")

    class Config:
        case_sensitive = True

settings = Settings()
