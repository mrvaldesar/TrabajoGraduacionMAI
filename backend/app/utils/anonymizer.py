import spacy
from app.core.config import settings

class Anonymizer:
    _nlp = None

    @classmethod
    def get_nlp(cls):
        if cls._nlp is None:
            try:
                cls._nlp = spacy.load(settings.SPACY_MODEL)
            except OSError:
                print(f"Warning: Spacy model '{settings.SPACY_MODEL}' not found. Downloading...")
                from spacy.cli import download
                download(settings.SPACY_MODEL)
                cls._nlp = spacy.load(settings.SPACY_MODEL)
        return cls._nlp

    @staticmethod
    def anonymize_text(text: str) -> str:
        """
        Reemplaza entidades nombradas en el texto con sus etiquetas (ej. [PER], [LOC]).
        """
        if not text:
            return ""

        nlp = Anonymizer.get_nlp()
        doc = nlp(text)

        # Reconstruimos el texto reemplazando entidades
        # Un enfoque más robusto usa offsets, pero por simplicidad reconstruiremos.
        # Nota: Esta reconstrucción simple podría perder matices de formato de espacios en blanco,
        # pero es suficiente para la lógica de procesamiento usualmente.
        # Alternativamente, podemos reemplazar en el lugar usando re.sub con offsets en orden inverso.

        anonymized_text = text
        # Procesar entidades en orden inverso para no alterar los índices
        for ent in reversed(doc.ents):
            # Queremos mantener entidades estándar como PER, LOC, ORG
            if ent.label_ in ["PER", "LOC", "ORG", "GPE", "DATE"]:
                replacement = f"<{ent.label_}>"
                anonymized_text = anonymized_text[:ent.start_char] + replacement + anonymized_text[ent.end_char:]

        return anonymized_text
