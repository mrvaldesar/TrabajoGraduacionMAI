import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    _beto_model = None
    _beto_tokenizer = None
    _sbert_model = None

    @classmethod
    def get_beto_model(cls):
        """
        Carga el modelo BETO para clasificación.
        Intenta cargar desde ruta local definida en settings.
        Recurre a un modelo base de HuggingFace si la ruta local no existe (propósitos de demo/dev).
        """
        if cls._beto_model is None:
            path = settings.BETO_MODEL_PATH
            try:
                if os.path.exists(path):
                    logger.info(f"Cargando modelo BETO desde ruta local: {path}")
                    cls._beto_tokenizer = AutoTokenizer.from_pretrained(path)
                    cls._beto_model = AutoModelForSequenceClassification.from_pretrained(path)
                else:
                    logger.warning(f"Modelo BETO local no encontrado en {path}. Usando modelo base 'dccuchile/bert-base-spanish-wwm-cased' para demostración.")
                    # Nota: Usar el modelo base para clasificación no funcionará para inferencia real sin cabezales fine-tuned,
                    # pero permite que el código se ejecute. En un escenario real, esto debería fallar o usar un modelo público específico.
                    # Usaremos el modelo base solo para instanciar la estructura de la clase.
                    base_model_name = "dccuchile/bert-base-spanish-wwm-cased"
                    cls._beto_tokenizer = AutoTokenizer.from_pretrained(base_model_name)
                    # Usar AutoModelForSequenceClassification con num_labels=6 (ejemplo) si solo cargamos base
                    cls._beto_model = AutoModelForSequenceClassification.from_pretrained(base_model_name, num_labels=6) # Etiquetas arbitrarias para demo
            except Exception as e:
                logger.error(f"Error cargando modelo BETO: {e}")
                raise e

        return cls._beto_tokenizer, cls._beto_model

    @classmethod
    def get_sbert_model(cls):
        """
        Carga el modelo Sentence-BERT para similitud.
        """
        if cls._sbert_model is None:
            path = settings.SBERT_MODEL_PATH
            try:
                # SentenceTransformer maneja rutas locales y nombres de modelos HF automáticamente
                logger.info(f"Cargando modelo S-BERT desde: {path}")
                cls._sbert_model = SentenceTransformer(path)
            except Exception as e:
                logger.error(f"Error cargando modelo S-BERT: {e}")
                raise e
        return cls._sbert_model
