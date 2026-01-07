import logging
from pathlib import Path

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
)
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    _beto_cls = None
    _beto_cls_tokenizer = None

    _beto_ner = None
    _beto_ner_tokenizer = None

    _sbert = None

    # ---------- BETO CLASIFICACIÓN (LOCAL OBLIGATORIO) ----------
    @classmethod
    def get_beto_cls(cls):
        if cls._beto_cls:
            return cls._beto_cls_tokenizer, cls._beto_cls

        path = Path(settings.BETO_MODEL_PATH)

        if not path.exists():
            raise RuntimeError(f"❌ Modelo BETO fine-tuned no encontrado en {path}")

        logger.info(f"✅ Cargando BETO clasificación desde {path}")

        cls._beto_cls_tokenizer = AutoTokenizer.from_pretrained(
            path, local_files_only=True
        )
        cls._beto_cls = AutoModelForSequenceClassification.from_pretrained(
            path, local_files_only=True
        )

        return cls._beto_cls_tokenizer, cls._beto_cls

    # ---------- BETO NER (LOCAL → DESCARGA SI FALTA) ----------
    @classmethod
    def get_beto_ner(cls):
        if cls._beto_ner:
            return cls._beto_ner

        path = Path(settings.BETO_NER_PATH)
        hf_id = settings.BETO_NER_HF_ID

        if path.exists() and any(path.iterdir()):
            logger.info(f"🔁 Cargando modelo NER desde disco: {path}")
            tokenizer = AutoTokenizer.from_pretrained(
                path, local_files_only=True
            )
            model = AutoModelForTokenClassification.from_pretrained(
                path, local_files_only=True
            )
        else:
            logger.info(f"⬇️ Descargando modelo NER desde HF: {hf_id}")
            tokenizer = AutoTokenizer.from_pretrained(hf_id)
            model = AutoModelForTokenClassification.from_pretrained(hf_id)

            logger.info(f"💾 Guardando modelo NER en disco: {path}")
            path.mkdir(parents=True, exist_ok=True)
            tokenizer.save_pretrained(path)
            model.save_pretrained(path)

        cls._beto_ner = (tokenizer, model)
        return cls._beto_ner

    # ---------- SBERT (LOCAL OBLIGATORIO) ----------
    @classmethod
    def get_sbert(cls):
        if cls._sbert:
            return cls._sbert

        path = Path(settings.SBERT_MODEL_PATH)

        if not path.exists():
            raise RuntimeError(f"❌ Modelo SBERT no encontrado en {path}")

        logger.info(f"✅ Cargando SBERT desde {path}")

        cls._sbert = SentenceTransformer(
            str(path),
            local_files_only=True,
            tokenizer_kwargs={"fix_mistral_regex": True},
        )


        return cls._sbert
