from pydantic import BaseModel

class ClassificationResponse(BaseModel):
    category: str
    confidence: float

class SimilarityResponse(BaseModel):
    similarity: float
    is_duplicate: bool

class ErrorResponse(BaseModel):
    detail: str
