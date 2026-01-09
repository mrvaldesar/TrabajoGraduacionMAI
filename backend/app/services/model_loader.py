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

    @classmethod
    def get_models_metadata(cls):
        """
        Recupera metadatos detallados de los modelos cargados.
        """
        metadata_list = []

        # 1. BETO Clasificación
        try:
            tokenizer, model = cls.get_beto_cls()
            cfg = model.config
            beto_meta = {
                "name": "BETO Fine-Tuned (Classification)",
                "type": "Sequence Classification",
                "description": "Modelo BERT pre-entrenado en español y ajustado para clasificar documentos administrativos.",
                "path": settings.BETO_MODEL_PATH,
                "metadata": {
                    "architecture": cfg.architectures[0] if cfg.architectures else "BertForSequenceClassification",
                    "vocab_size": cfg.vocab_size,
                    "hidden_size": cfg.hidden_size,
                    "num_hidden_layers": cfg.num_hidden_layers,
                    "num_attention_heads": cfg.num_attention_heads,
                    "max_position_embeddings": cfg.max_position_embeddings,
                    "num_labels": len(cfg.id2label) if hasattr(cfg, 'id2label') and cfg.id2label else "Unknown",
                    "model_type": cfg.model_type
                }
            }
            metadata_list.append(beto_meta)
        except Exception as e:
            logger.error(f"Error extrayendo metadata de BETO CLS: {e}")
            metadata_list.append({
                "name": "BETO Fine-Tuned (Classification)",
                "type": "Error",
                "description": "No se pudo cargar la información del modelo.",
                "path": settings.BETO_MODEL_PATH,
                "metadata": {"error": str(e)}
            })

        # 2. SBERT
        try:
            sbert = cls.get_sbert()
            # SBERT envuelve un Transformer (generalmente el primer módulo)
            # Intentamos acceder al AutoModel subyacente
            transformer_module = sbert._first_module().auto_model
            cfg = transformer_module.config

            sbert_meta = {
                "name": "Sentence-BERT (Similarity)",
                "type": "Sentence Embeddings",
                "description": "Modelo siamés para generar embeddings de oraciones y calcular similitud semántica (Coseno).",
                "path": settings.SBERT_MODEL_PATH,
                "metadata": {
                     "base_model": cfg._name_or_path,
                     "architecture": cfg.architectures[0] if cfg.architectures else "BertModel",
                     "vocab_size": cfg.vocab_size,
                     "hidden_size": cfg.hidden_size,
                     "max_sequence_length": sbert.max_seq_length,
                     "embedding_dimension": sbert.get_sentence_embedding_dimension(),
                     "pooling_mode": str(sbert._last_module())  # Usually Pooling module
                }
            }
            metadata_list.append(sbert_meta)
        except Exception as e:
            logger.error(f"Error extrayendo metadata de SBERT: {e}")
            metadata_list.append({
                "name": "Sentence-BERT (Similarity)",
                "type": "Error",
                "description": "No se pudo cargar la información del modelo.",
                "path": settings.SBERT_MODEL_PATH,
                "metadata": {"error": str(e)}
            })

        # 3. BETO NER
        try:
            tokenizer, model = cls.get_beto_ner()
            cfg = model.config
            ner_meta = {
                "name": "BETO NER (Anonymization)",
                "type": "Token Classification",
                "description": "Modelo BERT ajustado para reconocimiento de entidades nombradas (NER) para anonimización.",
                "path": settings.BETO_NER_PATH,
                "metadata": {
                    "architecture": cfg.architectures[0] if cfg.architectures else "BertForTokenClassification",
                    "vocab_size": cfg.vocab_size,
                    "hidden_size": cfg.hidden_size,
                    "num_labels": len(cfg.id2label) if hasattr(cfg, 'id2label') and cfg.id2label else "Unknown",
                    "labels": list(cfg.id2label.values()) if hasattr(cfg, 'id2label') and cfg.id2label else [],
                    "model_type": cfg.model_type
                }
            }
            metadata_list.append(ner_meta)
        except Exception as e:
            logger.error(f"Error extrayendo metadata de BETO NER: {e}")
            metadata_list.append({
                "name": "BETO NER (Anonymization)",
                "type": "Error",
                "description": "No se pudo cargar la información del modelo.",
                "path": settings.BETO_NER_PATH,
                "metadata": {"error": str(e)}
            })

        return metadata_list
