import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "API Trabajo de Graduación"
    API_V1_STR: str = "/api/v1"

    # Model Paths
    # Default to local folder structure, can be overridden by env vars

    # Modelo BETO para Clasificación de Documentos (Fine-tuned)
    BETO_MODEL_PATH: str = os.getenv("BETO_CLS_PATH", "models/beto_finetuned")

    # Modelo Sentence-BERT para Similitud Semántica
    SBERT_MODEL_PATH: str = os.getenv("SBERT_PATH", "models/sbert")

    # Modelo BETO para Reconocimiento de Entidades Nombradas (NER) - Ruta local
    BETO_NER_PATH: str = os.getenv("BETO_NER_PATH", "model_cache")

    # ID del modelo NER en Hugging Face (para descarga automática)
    BETO_NER_HF_ID: str = os.getenv("BETO_NER_HF_ID", "mrm8488/bert-spanish-cased-finetuned-ner")

    class Config:
        case_sensitive = True

settings = Settings()
