import io
import magic
import pdfplumber
import docx

class FileParser:
    @staticmethod
    def identify_mime_type(file_content: bytes) -> str:
        """Detecta el tipo MIME del contenido del archivo."""
        mime = magic.Magic(mime=True)
        return mime.from_buffer(file_content)

    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        """
        Extrae texto de varios formatos de archivo (PDF, DOCX, TXT).
        Detecta el tipo por mime-type o extensión.
        """
        # Primero intenta detectar por extensión como pista, pero usa mime para validación
        mime_type = FileParser.identify_mime_type(file_content)

        if mime_type == 'application/pdf':
            return FileParser._read_pdf(file_content)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return FileParser._read_docx(file_content)
        elif mime_type.startswith('text/'):
            return FileParser._read_txt(file_content)
        else:
            # Fallback basado en extensión si la detección mime es ambigua o genérica
            if filename.lower().endswith('.pdf'):
                return FileParser._read_pdf(file_content)
            elif filename.lower().endswith('.docx'):
                return FileParser._read_docx(file_content)
            elif filename.lower().endswith('.txt'):
                return FileParser._read_txt(file_content)

            raise ValueError(f"Tipo de archivo no soportado: {mime_type} para el archivo {filename}")

    @staticmethod
    def _read_pdf(content: bytes) -> str:
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    @staticmethod
    def _read_docx(content: bytes) -> str:
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    @staticmethod
    def _read_txt(content: bytes) -> str:
        # Intenta decodificar con utf-8, fallback a latin-1
        try:
            return content.decode('utf-8').strip()
        except UnicodeDecodeError:
            return content.decode('latin-1').strip()
