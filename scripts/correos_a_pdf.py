import os
import base64
import re
import unicodedata
import html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from email.utils import parsedate_to_datetime

# ===================== CONFIG =====================
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CARPETA_PDF = "correos_pdf"
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))


if not os.path.exists(CARPETA_PDF):
    os.makedirs(CARPETA_PDF)

# Puedes cambiar las palabras clave aquí
CONSULTA = '(subject:solicitud OR subject:correspondencia)'

# ===================== FUNCIONES =====================

def limpiar_nombre(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre)

def limpiar_texto(texto):
    if not texto:
        return ""

    # Eliminar caracteres raros visibles
    texto = re.sub(r'[■�]', '', texto)

    # Convertir entidades HTML (&nbsp; &amp; etc)
    texto = html.unescape(texto)

    # Normalizar caracteres Unicode
    texto = unicodedata.normalize("NFKD", texto)

    # Limpiar espacios invisibles
    texto = texto.replace('\xa0', ' ')
    texto = texto.replace('\u200b', '')
    texto = texto.replace('\u200c', '')
    texto = texto.replace('\u200d', '')
    texto = texto.replace('\ufeff', '')

    # Normalizar saltos de línea
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')

    # Evitar muchísimos saltos seguidos
    texto = re.sub(r'\n{3,}', '\n\n', texto)

    return texto.strip()

def formatear_fecha(fecha_raw):
    try:
        fecha = parsedate_to_datetime(fecha_raw)

        # Formato deseado: 05/03/2021 11:52 AM
        return fecha.strftime("%d/%m/%Y %I:%M %p")
    except:
        return fecha_raw

def autenticar():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def obtener_header(headers, nombre):
    for header in headers:
        if header['name'] == nombre:
            return header['value']
    return ""


def obtener_texto(part):
    texto = ""

    if part.get('mimeType') == 'text/plain':
        data = part['body'].get('data')
        if data:
            raw = base64.urlsafe_b64decode(data)

            for encoding in ["utf-8", "latin-1", "ISO-8859-1", "cp1252"]:
                try:
                    texto += raw.decode(encoding)
                    break
                except:
                    continue


    elif part.get('parts'):
        for subpart in part.get('parts', []):
            texto += obtener_texto(subpart)

    return texto


def crear_pdf(asunto, fecha, remitente, contenido):
    nombre_archivo = limpiar_nombre(asunto)

    if not nombre_archivo.strip():
        nombre_archivo = "Correo_sin_asunto"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(CARPETA_PDF, f"{timestamp}_{nombre_archivo}.pdf")

    c = canvas.Canvas(ruta, pagesize=letter)
    width, height = letter

    # Encabezado
    c.setFont("DejaVu", 12)
    c.drawString(40, height - 40, f"Asunto: {asunto}")
    c.setFont("DejaVu", 10)
    c.drawString(40, height - 60, f"Fecha: {fecha}")
    c.drawString(40, height - 75, f"De: {remitente}")

    y = height - 110
    c.setFont("DejaVu", 10)

    for linea in contenido.split('\n'):
        if y <= 40:
            c.showPage()
            c.setFont("DejaVu", 10)
            y = height - 40

        max_chars = 90
        while len(linea) > max_chars:
            c.drawString(40, y, linea[:max_chars])
            linea = linea[max_chars:]
            y -= 14

        c.drawString(40, y, linea)
        y -= 14


    c.save()
    print(f"✅ PDF creado: {ruta}")


# ===================== PROCESO PRINCIPAL =====================
def convertir_correos_a_pdf():
    creds = autenticar()
    service = build('gmail', 'v1', credentials=creds)

    mensajes = []
    page_token = None

    while True:
        results = service.users().messages().list(
            userId='me',
            q=CONSULTA,
            pageToken=page_token,
            maxResults=100
        ).execute()

        print("DEBUG RESULTS:", results.keys())
        print("DEBUG mensajes página:", len(results.get('messages', [])))        

        mensajes.extend(results.get('messages', []))
        page_token = results.get('nextPageToken')

        if not page_token:
            print("DEBUG: No más páginas")
            break

    print(f"\n📨 TOTAL correos encontrados: {len(mensajes)}")

    for msg in mensajes:
        mail = service.users().messages().get(userId='me', id=msg['id']).execute()

        headers = mail['payload'].get('headers', [])

        asunto = obtener_header(headers, "Subject") or "Sin asunto"
        remitente = obtener_header(headers, "From")
        fecha_raw = obtener_header(headers, "Date")
        fecha = formatear_fecha(fecha_raw)

        cuerpo = obtener_texto(mail['payload'])
        cuerpo = limpiar_texto(cuerpo)

        if cuerpo and len(cuerpo) > 25:
            crear_pdf(asunto, fecha, remitente, cuerpo)
        else:
            print(f"⚠ Correo sin texto plano válido: {asunto}")

    
if __name__ == "__main__":
    convertir_correos_a_pdf()