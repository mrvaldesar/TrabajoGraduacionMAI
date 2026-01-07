import re
import torch
from transformers import pipeline
from app.services.model_loader import ModelLoader

class Anonymizer:
    _pipeline = None
    _tokenizer = None
    
    # Lista de entidades sensibles conocidas (Gazetteer)
    KNOWN_ENTITIES = {
        "PER": [
            "Rolando Valdes", "Rolando Valdés", "Rolando Valdez", "Carlos Sandoval", "Kevin Garcia", "Sandy Ramos", "Carlos Tiniguar", "Carlos Andy", "Spencer Samayoa", "Claudia Flores", "Sergio Pineda", "Alexander Castro", "Valdéz", "Jacobo Abril Ubico",  "Jacobo, Abril Ubico",  "Abril Ubico, Jacobo", "Andrea Toc", "Jonatan Batz", "Marco Tulio Duvón", "Marco Tulio", "Erika Luis Az", "Alberta Marin", "Jose Contreras", "Erick Fernando Saravia",
            "Sandy", "Rolando", "Spencer", "Kevin", "Martín", "Claudia", "Sergio", "Carlos", "Andy", "Jonatan", "Marco", "Duvón", "Erika", "Luis", "Marin", "Andrea", "Morales", "Lopez", "Obregon", "Marroquin", "Portillo", "Mynor", "Marroquin", "Perez", "José", "Contreras", "Jose", "Evelyn", "Buch", "Mirna", "Rodriguez",
            "Geoffrey Estiven Hernández", "Martin", "Dulce Alexandra Morales", "Lesther Veliz", "Alba Leticia Marin Ramirez", "Luis Orozco", "Lilian Padilla", "Josué Saravia", "Cesar Barragan", "Ferenc Szaszdi", "Jacobo Abril", "Jacobo", "Timoteo Tiniguar",
        ],
        "ORG": [
            "Liberty Networks", "Corporación Guatetalents", "Corporacion Guatetalents", "TIGO", "SAT", "Cable & Wireless", "Tigo Business", "COLUMBUS NETWORKS", "Liberty Latin America", "INTEGRACION DE INFORMACION, S.A.", "Terguatemala", "Colegio BM-PC", "Accesorios Globales",
            "CELTECH", "C&W", "Intelaf", "Intcomex", "Guatetalents", "MegaPrint", "TIGO", "Comcel", "Comunicaciones Celulares", "Guatex", "Comunicaciones Celulares, Sociedad Anónima", "Tigo Business",
            "Liberty", "COLUMBUS", "cwcbusiness.com", "IntegraSAP", "SAP AG",
            "Superintendencia de Administración Tributaria", "Superintendencia de Administracion Tributaria"
        ],
        "LOC": [
            "Guatemala", "Zacapa", "Jutiapa", "Escuintla", "Esquipulas", "Ciudad de Guatemala",
            "Poptun", "Santa Elena", "Sayaxche", "Barberena", "Izabal", "Santa Rosa", "Petén",
            "Edificio Buró", "Plaza Buró", "Europlaza", "Oficina 1701", "Zona 10", 
        ]
    }

    @classmethod
    def load_models(cls):
        """
        Carga el modelo y el tokenizer en memoria si no existen (Singleton).
        """
        if cls._pipeline is None or cls._tokenizer is None:
            print(f"Cargando modelo NER...")
            device = 0 if torch.cuda.is_available() else -1
            
            try:
                # Usar ModelLoader para gestionar carga local vs descarga
                tokenizer, model = ModelLoader.get_beto_ner()
                cls._pipeline = pipeline(
                    "ner",
                    model=model,
                    tokenizer=tokenizer,
                    aggregation_strategy="simple",
                    device=device
                )
                cls._tokenizer = tokenizer
                print("✅ Modelo y tokenizer cargados correctamente.")
            except Exception as e:
                print(f"Error cargando el modelo: {e}")
                # Aquí podrías lanzar una excepción crítica si la API no puede vivir sin esto
                raise e

    @staticmethod
    def _anonymize_with_rules(text: str) -> str:
        """
        Aplica reglas de expresiones regulares (Regex) para patrones fijos.
        """
        if not text:
            return ""

        # 1. URLs
        text = re.sub(r'\b(?:https?://|www\.)[^\s]+\b', '[SITIO_WEB]', text, flags=re.IGNORECASE)

        # 2. Correos
        text = re.sub(r'<\s*[A-Za-z0-9._%+-]+@(?![EMPRESA])([A-Za-z0-9.-]+\.[A-Za-z]{2,})\s*>', '<[CORREO]>', text)
        text = re.sub(r'[A-Za-z0-9._%+-]+@(?![EMPRESA])([A-Za-z0-9.-]+\.[A-Za-z]{2,})', '[CORREO]', text)

        # 3. Direcciones (tolerante, Guatemala + OCR)
        text = re.sub(
            r'\b(?:'
            r'\d{1,2}\s*(?:[Aa]|\d{1,2}[aA])?\s*'                     # 6a, 6 A, 10
            r'(?:Calle|Cal(le)?|Avenida|Av\.?|Ave\.?|Aven(?:ida)?|'
            r'Calzada|Calz\.?|Blvd\.?|Boulevard|Boulevar|'
            r'Carretera|Carr\.?|Ruta|Km\.?)'
            r'[\s,]+'
            r'[A-Za-z0-9#.\-“”"\-\/\s]+?'                             # nombre / número
            r'|'
            r'(?:Zona|Z0na)\s*\d{1,2}'                                # Zona 1, Z0na 10
            r'|'
            r'Km\.?\s*\d+(?:\.\d+)?'                                  # Km 14.5
            r')'
            r'(?:[\s,]+(?:'
            r'Zona|Z0na|Col\.?|Colonia|Residenciales?|'
            r'Edificio|Torre|Oficina|Apto\.?|Apartamento|'
            r'Casa|Nivel|Piso'
            r')[\s#]*\w+)*',
            '[DIRECCION]', text, flags=re.IGNORECASE
        )

        # 4. DPI
        text = re.sub(r'\b\d{4}(?:[-\s]?\d{5})(?:[-\s]?\d{4})\b', '[DPI]', text)

        # 5. NIT
        text = re.sub(r'(NIT\.?\s*:?\s*)\d{6,9}(?:[-\s]?[0-9Kk])?', r'\1[NIT]', text, flags=re.IGNORECASE)
        
        # 6. Teléfonos
        text = re.sub(r'\b(?:\+?502[\s-]?)?[2456]\d{3}[\s-]\d{4}\b', '[TELEFONO]', text)

        # 7. Montos
        text = re.sub(r'\b(?:[QUS]\.?[\s]?\$?[\s]?[A-Za-z0-9.,]+(?:\s?[\d,]*\.\d{1,2})?|S\$\s?\d+(?:[\s,]?\d{3})*(?:\.\d{1,2})?|¥\s?\d+(?:[\s,]?\d{3})*(?:\.\d{1,2})?)\b', '[MONTO]', text)

        # 8. Códigos
        text = re.sub(r'\b[A-Z]{2,4}\d{2,4}-?\d{4,10}\b', '[CODIGO]', text)

        # 9. Fechas
        text = re.sub(
            r'\b('
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            r'|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
            r'|\d{1,2}\s*(?:de\s*)?(?:ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun(?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:tiembre)?|set(?:iembre)?|oct(?:ubre)?|nov(?:iembre)?|dic(?:iembre)?)\s*(?:de\s*)?\d{2,4}'
            r'|\d{1,2}[A-Z]{3}\s*\d{4}'
            r')'
            r'(?:\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)?'
            r'\b',
            '[FECHA]', text, flags=re.IGNORECASE
        )

        return text

    @classmethod
    def _apply_ner_replacement(cls, text_fragment: str) -> str:
        """
        Aplica NER al fragmento y reemplaza entidades detectadas.
        """
        try:
            # Aseguramos que el pipeline esté cargado
            cls.load_models()
            entities = cls._pipeline(text_fragment)
            
            # Reemplazo en reverso para no afectar índices
            for ent in reversed(entities):
                start = ent["start"]
                end = ent["end"]
                group = ent["entity_group"]
                
                replacement = None
                if group == "PER":
                    replacement = "[PERSONA]"
                elif group == "ORG":
                    replacement = "[EMPRESA]"
                elif group in ["LOC", "MISC"]:
                    replacement = "[LUGAR]"
                
                if replacement:
                    text_fragment = text_fragment[:start] + replacement + text_fragment[end:]
                    
        except Exception as e:
            print(f"Error procesando fragmento NER: {e}")
            pass
            
        return text_fragment

    @classmethod
    def anonymize_text(cls, text: str) -> str:
        """
        Método principal que orquesta la anonimización Híbrida:
        Diccionario -> Reglas Regex -> Modelo NER con Chunking.
        """
        if not text:
            return ""

        # Aseguramos carga de modelos antes de procesar cualquier cosa
        cls.load_models()

        # Paso 1: Gazetteer (Diccionario conocido)
        entity_map = {"PER": "[PERSONA]", "ORG": "[EMPRESA]", "LOC": "[LUGAR]"}
        for label, items in cls.KNOWN_ENTITIES.items():
            if label not in entity_map:
                continue
            replacement = entity_map[label]
            # Ordenamos por longitud descendente para evitar reemplazos parciales incorrectos
            items_sorted = sorted(items, key=len, reverse=True)
            for item in items_sorted:
                # Usamos re.escape para evitar problemas con caracteres especiales
                pattern = r'\b' + re.escape(item) + r'\b'
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Paso 2: Reglas Regex
        text = cls._anonymize_with_rules(text)

        # Paso 3: BETO-NER con Chunking (Ventana deslizante)
        all_tokens = cls._tokenizer.encode(text, add_special_tokens=False)
        
        # Si el texto es corto, procesamos directo
        if len(all_tokens) < 500:
            text = cls._apply_ner_replacement(text)
        else:
            # Procesamiento por bloques para textos largos
            processed_fragments = []
            window_size = 500
            
            for i in range(0, len(all_tokens), window_size):
                chunk_ids = all_tokens[i : i + window_size]
                # decode puede perder espaciado original, pero es necesario para el chunking lógico actual
                chunk_text = cls._tokenizer.decode(chunk_ids, skip_special_tokens=True)
                processed_chunk = cls._apply_ner_replacement(chunk_text)
                processed_fragments.append(processed_chunk)
            
            # Unimos los fragmentos
            text = " ".join(processed_fragments)

        return text