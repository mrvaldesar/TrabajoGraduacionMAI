from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from app.api.schemas import ClassificationResponse, SimilarityResponse, ErrorResponse, ModelsResponse
from app.utils.file_parser import FileParser
from app.utils.anonymizer import Anonymizer
from app.services.nlp_engine import NLPEngine
from app.services.model_loader import ModelLoader
import logging
import time

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
        t0 = time.perf_counter()
        clean_text = Anonymizer.anonymize_text(text)
        t1 = time.perf_counter()
        anon_time = t1 - t0

        # Clasificación
        t2 = time.perf_counter()
        result = NLPEngine.classify_text(clean_text)
        t3 = time.perf_counter()
        inf_time = t3 - t2

        return ClassificationResponse(
            category=result["category"],
            confidence=result["confidence"],
            inference_time=inf_time,
            anonymization_time=anon_time
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
        t0 = time.perf_counter()
        clean_text1 = Anonymizer.anonymize_text(text1)
        clean_text2 = Anonymizer.anonymize_text(text2)
        t1 = time.perf_counter()
        anon_time = t1 - t0

        # Similitud
        t2 = time.perf_counter()
        score = NLPEngine.compute_similarity(clean_text1, clean_text2)
        t3 = time.perf_counter()
        inf_time = t3 - t2

        # Lógica de duplicidad: is_duplicate = true si similarity >= 0.90
        is_dup = score >= 0.90

        return SimilarityResponse(
            similarity=score,
            is_duplicate=is_dup,
            inference_time=inf_time,
            anonymization_time=anon_time
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en similitud: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=ModelsResponse)
def get_models_info():
    """
    Endpoint para obtener metadatos de los modelos cargados.
    """
    try:
        data = ModelLoader.get_models_metadata()
        return ModelsResponse(models=data)
    except Exception as e:
        logger.error(f"Error obteniendo info de modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
