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

@router.post(
    "/classify",
    response_model=ClassificationResponse,
    tags=["NLP Operations"],
    summary="Clasificar Documento",
    description="""
    Recibe un archivo de texto (`.txt`), lo procesa y determina a qué categoría pertenece.

    **Flujo de Proceso:**
    1. **Extracción**: Lee el contenido del archivo.
    2. **Anonimización**: Detecta y ofusca entidades sensibles (nombres, fechas, etc.) usando NER.
    3. **Inferencia**: Utiliza un modelo **BETO** fine-tuned para predecir la categoría.
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Archivo vacío o sin texto legible."},
        415: {"model": ErrorResponse, "description": "Tipo de archivo no soportado (debe ser .txt)."},
        500: {"model": ErrorResponse, "description": "Error interno del servidor durante el procesamiento."}
    }
)
def classify_document(file: UploadFile = File(..., description="Archivo de texto a clasificar (.txt)")):
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
            anonymization_time=anon_time,
            anonymized_text=clean_text
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en clasificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/similarity",
    response_model=SimilarityResponse,
    tags=["NLP Operations"],
    summary="Comparar Documentos (Similitud)",
    description="""
    Compara dos archivos de texto para calcular su similitud semántica y detectar posibles duplicados.

    **Flujo de Proceso:**
    1. **Extracción**: Lee el contenido de ambos archivos.
    2. **Anonimización**: Ofusca entidades sensibles en ambos textos.
    3. **Inferencia**: Genera embeddings con **S-BERT** y calcula la similitud del coseno.

    *Nota: Se considera duplicado si la similitud es >= 0.85.*
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Uno o ambos archivos no contienen texto válido."},
        415: {"model": ErrorResponse, "description": "Tipo de archivo no soportado (debe ser .txt)."},
        500: {"model": ErrorResponse, "description": "Error interno del servidor."}
    }
)
def compare_documents(
    file1: UploadFile = File(..., description="Primer archivo de texto (.txt)"),
    file2: UploadFile = File(..., description="Segundo archivo de texto (.txt)")
):
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
        is_dup = score >= 0.85

        return SimilarityResponse(
            similarity=score,
            is_duplicate=is_dup,
            inference_time=inf_time,
            anonymization_time=anon_time,
            anonymized_text_1=clean_text1,
            anonymized_text_2=clean_text2
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en similitud: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/models",
    response_model=ModelsResponse,
    tags=["System Info"],
    summary="Información de Modelos",
    description="Devuelve metadatos técnicos sobre los modelos de IA cargados actualmente en la memoria del servidor.",
    responses={
        500: {"model": ErrorResponse, "description": "Error al recuperar metadatos de los modelos."}
    }
)
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
