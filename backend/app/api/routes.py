from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from app.api.schemas import ClassificationResponse, SimilarityResponse, ErrorResponse
from app.utils.file_parser import FileParser
from app.utils.anonymizer import Anonymizer
from app.services.nlp_engine import NLPEngine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/classify", response_model=ClassificationResponse)
def classify_document(file: UploadFile = File(...)):
    """
    Endpoint para clasificar un documento.
    1. Lee el archivo (solo TXT).
    2. Anonimiza el contenido.
    3. Pasa el texto anonimizado al modelo BETO.
    """
    try:
        content = file.file.read()
        text = FileParser.extract_text(content, file.filename)

        if not text:
             raise HTTPException(status_code=400, detail="El archivo está vacío o no se pudo extraer texto.")

        # Anonimización
        clean_text = Anonymizer.anonymize_text(text)

        # Clasificación
        result = NLPEngine.classify_text(clean_text)

        return ClassificationResponse(
            category=result["category"],
            confidence=result["confidence"]
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en clasificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/similarity", response_model=SimilarityResponse)
def compare_documents(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Endpoint para calcular similitud semántica entre dos documentos.
    1. Lee ambos archivos.
    2. Anonimiza ambos textos.
    3. Calcula similitud con S-BERT.
    """
    try:
        content1 = file1.file.read()
        content2 = file2.file.read()

        text1 = FileParser.extract_text(content1, file1.filename)
        text2 = FileParser.extract_text(content2, file2.filename)

        if not text1 or not text2:
             raise HTTPException(status_code=400, detail="Uno de los archivos no contiene texto extraíble.")

        # Anonimización
        clean_text1 = Anonymizer.anonymize_text(text1)
        clean_text2 = Anonymizer.anonymize_text(text2)

        # Similitud
        score = NLPEngine.compute_similarity(clean_text1, clean_text2)

        # Lógica de duplicidad: is_duplicate = true si similarity >= 0.90
        is_dup = score >= 0.90

        return SimilarityResponse(
            similarity=score,
            is_duplicate=is_dup
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en similitud: {e}")
        raise HTTPException(status_code=500, detail=str(e))
