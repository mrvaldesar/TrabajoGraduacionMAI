FROM python:3.10-slim

# --- Variables de entorno ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/model_cache
ENV TRANSFORMERS_CACHE=/model_cache
ENV HF_HUB_DISABLE_TELEMETRY=1

WORKDIR /app

# --- Dependencias del sistema ---
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# --- Dependencias Python ---
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# --- Pre-cargar BETO NER (modelo HF) para acelerar primer arranque ---
RUN python -c "from transformers import AutoTokenizer, AutoModelForTokenClassification; \
    model_name='mrm8488/bert-spanish-cased-finetuned-ner'; \
    print(f'Pre-cargando modelo NER: {model_name}'); \
    AutoTokenizer.from_pretrained(model_name); \
    AutoModelForTokenClassification.from_pretrained(model_name)"

# --- Copiar el código de la app ---
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
