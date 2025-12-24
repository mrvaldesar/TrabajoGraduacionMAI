import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CARPETA_DESCARGA = "adjuntos_correspondencia"

if not os.path.exists(CARPETA_DESCARGA):
    os.makedirs(CARPETA_DESCARGA)

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

def descargar_adjuntos():
    creds = autenticar()
    service = build('gmail', 'v1', credentials=creds)

    query = "subject:RRHH has:attachment" #### Responsabilidad Aceptacion 
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    print(f"Correos encontrados: {len(messages)}")

    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()

        for part in message['payload'].get('parts', []):
            if part.get('filename') and part.get('body') and part['body'].get('attachmentId'):
                filename = part['filename']
                attachment_id = part['body']['attachmentId']

                attachment = service.users().messages().attachments().get(
                    userId='me',
                    messageId=msg['id'],
                    id=attachment_id
                ).execute()

                file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                ruta = os.path.join(CARPETA_DESCARGA, filename)
                with open(ruta, "wb") as f:
                    f.write(file_data)

                print(f"✅ Descargado: {filename}")

if __name__ == "__main__":
    descargar_adjuntos()
