from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ClassificationResponse(BaseModel):
    category: str = Field(
        ...,
        description="Categoría predicha para el documento.",
        examples=["Contratos"]
    )
    confidence: float = Field(
        ...,
        description="Nivel de confianza de la predicción (0.0 a 1.0).",
        examples=[0.98]
    )
    inference_time: float = Field(
        ...,
        description="Tiempo tomado por el modelo para clasificar (segundos).",
        examples=[0.15]
    )
    anonymization_time: float = Field(
        ...,
        description="Tiempo tomado para anonimizar el texto antes de la inferencia (segundos).",
        examples=[0.05]
    )
    anonymized_text: str = Field(
        ...,
        description="Texto extraído y anonimizado utilizado para la clasificación.",
        examples=["El presente contrato de servicios..."]
    )

class SimilarityResponse(BaseModel):
    similarity: float = Field(
        ...,
        description="Puntuación de similitud semántica (0.0 a 1.0).",
        examples=[0.95]
    )
    is_duplicate: bool = Field(
        ...,
        description="Indica si los documentos se consideran duplicados (similitud >= 0.90).",
        examples=[True]
    )
    inference_time: float = Field(
        ...,
        description="Tiempo tomado para calcular la similitud (segundos).",
        examples=[0.22]
    )
    anonymization_time: float = Field(
        ...,
        description="Tiempo total de anonimización para ambos documentos (segundos).",
        examples=[0.08]
    )
    anonymized_text_1: str = Field(
        ...,
        description="Texto anonimizado del primer documento.",
        examples=["Texto documento 1..."]
    )
    anonymized_text_2: str = Field(
        ...,
        description="Texto anonimizado del segundo documento.",
        examples=["Texto documento 2..."]
    )

class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Descripción detallada del error.",
        examples=["El archivo está vacío o no es un formato válido."]
    )

class ModelMetadata(BaseModel):
    name: str = Field(..., description="Nombre identificador del modelo.", examples=["BETO Classification"])
    type: str = Field(..., description="Tipo de tarea del modelo.", examples=["classification"])
    description: str = Field(..., description="Descripción funcional del modelo.")
    path: str = Field(..., description="Ruta local o identificador del modelo.")
    metadata: Dict[str, Any] = Field(..., description="Metadatos técnicos adicionales (vocabulario, arquitectura, labels).")

class ModelsResponse(BaseModel):
    models: List[ModelMetadata] = Field(..., description="Lista de modelos cargados en el sistema.")
