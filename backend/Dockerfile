# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Establecemos el directorio de caché de HF dentro de la app para permisos controlados
ENV HF_HOME=/app/model_cache

# Set work directory
WORKDIR /app

# Install system dependencies
# libmagic1 is required for python-magic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    # 1. Instalamos Torch CPU explícitamente primero
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    # 2. Instalamos el resto. Si borraste 'spacy' del txt, se instalará todo rápido.
    pip install --no-cache-dir -r requirements.txt

# --- OPTIMIZACIÓN CRÍTICA: PRE-CARGA DEL MODELO NER ---
# Ejecutamos un script inline para descargar el modelo y el tokenizer durante el BUILD.
# Esto guarda los archivos en la capa de la imagen Docker.
# Así, cuando inicie el contenedor, el modelo ya estará ahí (arranque instantáneo).
RUN python -c "from transformers import pipeline, AutoTokenizer; \
    model_name = 'mrm8488/bert-spanish-cased-finetuned-ner'; \
    print(f'Descargando {model_name}...'); \
    pipeline('ner', model=model_name, tokenizer=model_name); \
    AutoTokenizer.from_pretrained(model_name);"

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]