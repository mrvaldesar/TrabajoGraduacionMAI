from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from app.main import app
# Importamos Routes para patchear correctamente NLPEngine si fuera necesario,
# pero dado que routes importa NLPEngine de services, patch("app.services.nlp_engine.NLPEngine") debería funcionar
# si se hace correctamente.
# Sin embargo, en la ejecución anterior vimos que no funcionó con app.services... en el primer intento.
# Vamos a usar patch sobre 'app.api.routes.NLPEngine' que es donde se usa.

client = TestClient(app)

# Dummy file content
TXT_CONTENT = b"Este es un archivo de prueba. Mi nombre es Juan Perez y vivo en Santiago."

@pytest.fixture(autouse=True)
def mock_nlp_engine():
    # Patch sobre el objeto importado en routes.py
    with patch("app.api.routes.NLPEngine") as mock:
        mock.classify_text.return_value = {
            "category": "Contratos",
            "confidence": 0.95
        }
        mock.compute_similarity.return_value = 0.99
        yield mock

def test_read_main():
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

def test_classify_endpoint_txt():
    file_name = "test.txt"
    files = {"file": (file_name, TXT_CONTENT, "text/plain")}

    response = client.post("/api/v1/classify", files=files)

    assert response.status_code == 200
    data = response.json()

    assert "category" in data
    assert isinstance(data["category"], str)
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert "anonymized_text" in data
    assert isinstance(data["anonymized_text"], str)

def test_similarity_endpoint_txt():
    files = [
        ("file1", ("doc1.txt", b"El perro corre en el parque.", "text/plain")),
        ("file2", ("doc2.txt", b"El canino juega en el jardin.", "text/plain"))
    ]

    response = client.post("/api/v1/similarity", files=files)

    assert response.status_code == 200
    data = response.json()

    assert "similarity" in data
    assert isinstance(data["similarity"], float)
    assert 0.0 <= data["similarity"] <= 1.0
    assert "is_duplicate" in data
    assert isinstance(data["is_duplicate"], bool)
    assert "anonymized_text_1" in data
    assert "anonymized_text_2" in data
    assert isinstance(data["anonymized_text_1"], str)
    assert isinstance(data["anonymized_text_2"], str)

def test_similarity_is_duplicate_logic():
    text = b"Texto identico para prueba de duplicidad."
    files = [
        ("file1", ("doc1.txt", text, "text/plain")),
        ("file2", ("doc2.txt", text, "text/plain"))
    ]

    response = client.post("/api/v1/similarity", files=files)
    data = response.json()

    assert data["similarity"] > 0.90
    assert data["is_duplicate"] is True

def test_empty_file():
    files = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/api/v1/classify", files=files)
    # Ahora que FileParser acepta x-empty y devuelve "", routes debe lanzar 400
    assert response.status_code == 400

def test_classify_endpoint_pdf_fail():
    file_name = "test.pdf"
    files = {"file": (file_name, b"%PDF-1.4...", "application/pdf")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 415
    data = response.json()
    assert "Tipo de archivo no soportado" in data["detail"]

def test_classify_endpoint_docx_fail():
    file_name = "test.docx"
    # Usamos un contenido ligeramente más realista para evitar falsos positivos de text/plain si magic es muy agresivo
    # Un zip file (docx) suele empezar con PK\x03\x04
    files = {"file": (file_name, b"PK\x03\x04\x14\x00\x06\x00", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}

    response = client.post("/api/v1/classify", files=files)

    assert response.status_code == 415
    data = response.json()
    assert "Tipo de archivo no soportado" in data["detail"]
