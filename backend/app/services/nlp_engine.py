import torch
from sentence_transformers import util
from app.services.model_loader import ModelLoader
import logging

logger = logging.getLogger(__name__)

class NLPEngine:

    # Etiquetas de respaldo en caso de que el modelo no tenga id2label configurado
    # o estemos usando el modelo base de fallback.
    FALLBACK_LABELS = {
        0: "Contratos",
        1: "Correos electrónicos",
        2: "Correspondencia administrativa",
        3: "Cotizaciones",
        4: "Documentos fiscales",
        5: "Recursos Humanos"
    }

    @staticmethod
    def classify_text(text: str):
        """
        Clasifica el texto usando el modelo BETO.
        Devuelve la categoría (str) y la confianza (float).
        """
        tokenizer, model = ModelLoader.get_beto_cls()

        # Tokenización
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

        # Inferencia
        with torch.no_grad():
            outputs = model(**inputs)

        # Procesar salida (Softmax)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        top_prob, top_label_idx = torch.max(probs, dim=1)
        idx = int(top_label_idx.item())
        confidence = float(top_prob.item())

        # Mapeo de etiqueta
        # Intentamos usar la config del modelo si tiene id2label
        category = "Desconocido"
        if hasattr(model.config, 'id2label') and model.config.id2label:
            # Pydantic/Transformers a veces usa keys string o int, nos aseguramos
            category = model.config.id2label.get(idx, model.config.id2label.get(str(idx)))

        # Si falló la obtención o no existe, usamos el fallback
        # (Esto ocurrirá si estamos usando el modelo base descargado al vuelo)
        # O si el modelo devuelve una etiqueta genérica tipo "LABEL_0"
        if not category or category.upper().startswith("LABEL_"):
            # Ajustamos el índice al rango de fallback (modulo len) para evitar crashes en demo con modelo base random
            safe_idx = idx % len(NLPEngine.FALLBACK_LABELS)
            category = NLPEngine.FALLBACK_LABELS[safe_idx]

        return {
            "category": category,
            "confidence": confidence
        }

    @staticmethod
    def compute_similarity(text1: str, text2: str) -> float:
        """
        Calcula la similitud semántica entre dos textos usando S-BERT.
        Devuelve un puntaje flotante entre 0 y 1.
        """
        model = ModelLoader.get_sbert()

        # Calcular embeddings
        embeddings1 = model.encode(text1, convert_to_tensor=True)
        embeddings2 = model.encode(text2, convert_to_tensor=True)

        # Calcular similitud coseno
        cosine_score = util.cos_sim(embeddings1, embeddings2)

        # Clamp value to [0, 1] just in case of floating point weirdness
        score = float(cosine_score.item())
        return max(0.0, min(1.0, score))
