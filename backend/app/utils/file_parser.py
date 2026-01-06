import io
import magic

class FileParser:
    @staticmethod
    def identify_mime_type(file_content: bytes) -> str:
        """Detecta el tipo MIME del contenido del archivo."""
        mime = magic.Magic(mime=True)
        return mime.from_buffer(file_content)

    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        """
        Extrae texto de archivos TXT.
        Valida que el archivo sea texto plano.
        """
        mime_type = FileParser.identify_mime_type(file_content)

        # Validamos que sea texto plano
        # Solo aceptamos si el mime es texto explícito o si la extensión es .txt Y el mime no es binario peligroso
        # Nota: libmagic a veces dice 'application/octet-stream' para texto ASCII muy corto o raro,
        # pero 'text/plain' es lo usual. Si el usuario sube un .txt que magic dice que es 'application/zip', debemos rechazarlo.

        is_text_mime = mime_type.startswith('text/')
        is_txt_ext = filename.lower().endswith('.txt')

        if is_text_mime:
             return FileParser._read_txt(file_content)

        if is_txt_ext and mime_type == 'text/plain':
             return FileParser._read_txt(file_content)

        # Si tiene extension .txt pero magic dice que NO es texto (ej: application/pdf), se rechaza.
        # Esto previene que alguien renombre test.pdf a test.txt y lo suba.

        # Caso especial: algunos archivos de texto vacíos o con encoding raro pueden ser identificados como inode/x-empty o similar
        if (mime_type == 'inode/x-empty' or mime_type == 'application/x-empty') and is_txt_ext:
             return ""

        raise ValueError(f"Tipo de archivo no soportado: {mime_type} para el archivo {filename}. Solo se permiten archivos de texto (*.txt).")

    @staticmethod
    def _read_txt(content: bytes) -> str:
        # Intenta decodificar con utf-8, fallback a latin-1
        try:
            return content.decode('utf-8').strip()
        except UnicodeDecodeError:
            return content.decode('latin-1').strip()
