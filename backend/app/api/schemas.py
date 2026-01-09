from pydantic import BaseModel

class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    inference_time: float
    anonymization_time: float

class SimilarityResponse(BaseModel):
    similarity: float
    is_duplicate: bool
    inference_time: float
    anonymization_time: float

class ErrorResponse(BaseModel):
    detail: str

class ModelMetadata(BaseModel):
    name: str
    type: str
    description: str
    path: str
    metadata: dict

class ModelsResponse(BaseModel):
    models: list[ModelMetadata]
