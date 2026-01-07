# API Rest Proyecto de Graduación

Este proyecto proporciona una API REST modular construida con **FastAPI** para la clasificación automática de documentos y el cálculo de similitud semántica.

## Características

*   **Framework**: FastAPI
*   **Modelos**:
    *   **Clasificación**: Utiliza **BETO fine-tunned** (BERT para español) para categorizar documentos.
    *   **Similitud**: Utiliza **S-BERT** (Sentence-BERT) para detectar duplicados o similitud semántica.
*   **Procesamiento de Archivos**: Soporte nativo para extraer texto de **.txt**.
*   **Anonimización**: Capa intermedia (middleware/utilidad), que usa una estrategia híbrida para anonimizar antes de ejecutar la inferencia.

## Requisitos

*   Python 3.9+
*   Dependencias del sistema: `libmagic1` (para detección de tipos de archivo).

## Instalación y Ejecución Local

1.  **Clonar el repositorio y entrar al directorio**:
    ```bash
    git clone https://github.com/mrvaldesar/TrabajoGraduacionMAI.git
    cd <repo-folder>/backend
    ```

2.  **Crear un entorno virtual e instalar dependencias**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configuración de Modelos (Opcional)**:
    El sistema busca modelos locales en las rutas definidas en `app/core/config.py`.
    *   `BETO_MODEL_PATH`: Por defecto `models/modelo_beto_finetuned_v1`, sino se usará `dccuchile/bert-base-spanish-wwm-cased`.
    *   `SBERT_MODEL_PATH`: Por defecto `models/modelo_sbert`.

    *Nota: Si no encuentra el modelo BETO local, el sistema descargará un modelo base de HuggingFace para permitir la demostración, aunque la clasificación no será precisa sin el fine-tuning.*

4.  **Iniciar el servidor**:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

    La API estará disponible en `http://localhost:8000`.

## Documentación de la API

Una vez iniciado el servidor, puedes acceder a la documentación interactiva (Swagger UI) en:
*   **URL**: `http://localhost:8000/docs`

### Endpoints Principales

#### 1. POST `/api/v1/classify`
Recibe un archivo y devuelve su categoría predicha.

*   **Input**: `file` (UploadFile - solo TXT)
*   **Output JSON**:
    ```json
    {
      "category": "Contratos",
      "confidence": 0.98
    }
    ```

#### 2. POST `/api/v1/similarity`
Recibe dos archivos y calcula su similitud semántica.

*   **Input**: `file1`, `file2` (UploadFile)
*   **Output JSON**:
    ```json
    {
      "similarity": 0.95,
      "is_duplicate": true
    }
    ```
    *Nota: `is_duplicate` es `true` si la similitud es >= 0.90.*

## Pruebas

Para ejecutar las pruebas de integración:

```bash
pytest tests/test_api.py
```
