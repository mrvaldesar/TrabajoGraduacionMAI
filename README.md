# Módulo de PLN para Clasificación y Detección Semántica de Documentos Empresariales

Este repositorio contiene los scripts y recursos del trabajo de graduación titulado **"Módulo de PLN para clasificación y detección semántica de documentos empresariales"**, desarrollado como parte del posgrado en Inteligencia Artificial en la Universidad Nacional de Ingeniería (UNI), Guatemala.

El proyecto busca **cerrar la brecha entre los avances académicos en Procesamiento del Lenguaje Natural (PLN) y su aplicación práctica en empresas guatemaltecas**, mediante la validación de modelos de lenguaje contextualizados (como BETO y Sentence-BERT) con documentos reales en español guatemalteco.

> 📌 **Nota**: Este repositorio incluye únicamente los componentes de preparación y procesamiento de datos. La API REST, el frontend y los modelos entrenados se gestionan en fases posteriores del desarrollo.

## Estructura del repositorio
```text
├── notebook/
│ ├── 0_eda.ipynb # Análisis exploratorio realizado
│ └── pln_clasificacion_duplicados_empresariales.ipynb # Anonimización de archivos y finetunning de modelos
│
├── scripts/
│ ├── descargar_adjuntos.py # Descarga archivos adjuntos de correos corporativos
│ ├── correos_a_pdf.py # Busca, descarga y convierte correos a PDF
│ ├── ftp_ocr_extractor.py # Extrae texto de documentos mediante OCR (para PDFs escaneados o imágenes)
│ ├── adjuntos_correspondencia/ # (Generada) Carpeta para adjuntos descargados
│ ├── correos_pdf/ # (Generada) Correos convertidos a PDF
│ └── extracted_files/ # (Generada) Texto plano extraído (listo para PLN)
│
├── backend   # API REST con FastAPI, Modelos NLP (BETO, S-BERT) y lógica de negocio.
└── frontend  # Aplicación de prueba, Web Angular para interactuar con los endpoints.
```

## Objetivo

Preparar un corpus documental realista y anonimizado, compuesto por **906 documentos empresariales** de una empresa guatemalteca del sector de telecomunicaciones, distribuidos en 6 categorías:
- Contratos
- Correos electrónicos
- Correspondencia administrativa
- Cotizaciones
- Documentos fiscales
- Documentos de Recursos Humanos

Estos datos servirán como base para:
- Entrenar y evaluar modelos de clasificación (BETO)
- Evaluar detección de duplicados semánticos (Sentence-BERT)
- Comparar contra un baseline tradicional (TF-IDF)

## Requisitos

- Python 3.10+
- Bibliotecas principales:
  - `imaplib`, `email` (procesamiento de correos)
  - `PyPDF2`, `pdf2image`, `python-docx` (manipulación de documentos)
  - `pytesseract`, `Pillow` (OCR con Tesseract)
  - `ftplib` (acceso a servidores FTP, si aplica)

> ⚠️ **Tesseract OCR debe estar instalado en el sistema**:  
> - Windows: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)  
> - Linux: `sudo apt install tesseract-ocr`

## Uso básico

1. **Configura credenciales** (correo, servidor FTP, etc.) en variables de entorno o archivo `.env`.
2. Ejecuta los scripts en orden según tu flujo de recolección:
   ```bash
   python scripts/descargar_adjuntos.py
   python scripts/correos_a_pdf.py
   python scripts/ftp_ocr_extractor.py
   ```
3. Los documentos procesados se guardarán en las carpetas correspondientes (correos_pdf/, extracted_files/, etc.), listos para su uso en el pipeline de PLN.
4. En la carpeta backend y frontend están las instrucciones correspondientes (README.md)

## Próximos pasos
- Mejorar manejo de volumenes docker para evitar descargar constantemente los modelos
- Preparar frontend
- Contenerizar y aplicar docker-compose.yml

## Licencia
Este proyecto tiene fines académicos y de investigación. El código está disponible bajo la licencia MIT.
Los documentos empresariales reales no se incluyen en este repositorio por confidencialidad.