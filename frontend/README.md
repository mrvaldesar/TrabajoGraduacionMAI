# Frontend - Prototipo de Investigación (NLP)

Este directorio contiene el código fuente de la aplicación web (Angular) desarrollada como parte del prototipo de investigación para el procesamiento de lenguaje natural.

La interfaz está diseñada para simular un entorno corporativo de escritorio ("Interfaz de Estilo ERP"), facilitando la interacción con los servicios de clasificación y similitud de documentos.

## Requisitos Previos

*   Node.js (versión 18+ recomendada)
*   NPM (incluido con Node.js)
*   Angular CLI (instalable vía `npm install -g @angular/cli`)

## Instalación y Ejecución

1.  **Instalar dependencias:**
    Navega a esta carpeta y ejecuta:
    ```bash
    npm install
    ```

2.  **Servidor de Desarrollo:**
    Inicia la aplicación localmente:
    ```bash
    ng serve
    ```
    La aplicación estará disponible en `http://localhost:4200/`.

3.  **Construcción para Producción:**
    Para generar los archivos estáticos optimizados:
    ```bash
    ng build
    ```
    Los artefactos de construcción se almacenarán en el directorio `dist/`.

## Ejecución con Docker

Si se prefiere ejecutar el frontend de forma aislada mediante Docker (sin usar docker-compose desde la raíz):

1.  **Construir la imagen:**
    ```bash
    docker build -t nlp-frontend .
    ```

2.  **Ejecutar el contenedor:**
    ```bash
    docker run -d -p 80:80 --name nlp-frontend nlp-frontend
    ```
    La aplicación estará disponible en `http://localhost`.

    *Nota:* Asegurarse de que el backend esté accesible. Si el backend corre en otro contenedor o en local, deberás configurar la URL de la API adecuadamente en `src/environments/environment.prod.ts` o mediante configuración de Nginx.

## Estructura del Proyecto

El código principal se encuentra bajo `src/app/`. Los módulos clave incluyen:

*   **Dashboard:** Visualización de estadísticas de uso (gráficos de Chart.js) basadas en datos locales.
*   **Clasificación:** Módulo de carga de archivos (PDF, DOCX, TXT, Imágenes) para inferencia de categorías.
*   **Similitud:** Interfaz para la comparación semántica de dos documentos ("Documento A" vs "Documento B").
*   **Historial:** Tabla de registros de operaciones guardadas en el almacenamiento local del navegador (`localStorage`).
*   **Modelos:** Vista informativa sobre los metadatos de los modelos NLP cargados en el backend.

### Servicios Clave

*   `FileConversionService`: Servicio crítico que orquesta la conversión de todos los formatos de entrada a texto plano (`.txt`) **en el cliente** antes de enviarlos al backend. Esto asegura que la API solo reciba un archivo de texto.

## Dependencias Principales

El frontend maneja una carga significativa de procesamiento de archivos gracias a las siguientes librerías:

*   **tesseract.js**: Motor OCR en WebAssembly para extraer texto de imágenes y PDFs escaneados.
*   **pdfjs-dist**: Parsing nativo de archivos PDF (capa de texto).
*   **mammoth**: Conversión de documentos `.docx` a texto.
*   **xlsx**: Lectura y extracción de datos de hojas de cálculo Excel.
*   **chart.js**: Renderizado de gráficos estadísticos en el Dashboard.

## Estilo Visual

La aplicación implementa una "Interfaz Corporativa de Escritorio" personalizada. Características principales:

*   **Navegación Lateral:** Una barra lateral fija para el menú principal.
*   **Formularios Horizontales:** Etiquetas alineadas a la izquierda de los campos de entrada para mejorar la legibilidad en pantallas de escritorio.
*   **Paleta de Colores:** Uso de tonos neutros (beige, gris) y encabezados azules para mantener una estética profesional y sobria.
