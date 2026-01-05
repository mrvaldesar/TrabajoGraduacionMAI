from fastapi.testclient import TestClient
from app.main import app
import pytest
import io
import os

client = TestClient(app)

# Dummy file content
TXT_CONTENT = b"Este es un archivo de prueba. Mi nombre es Juan Perez y vivo en Santiago."

def test_read_main():
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

def test_classify_endpoint_txt():
    # Test uploading a text file
    file_name = "test.txt"
    files = {"file": (file_name, TXT_CONTENT, "text/plain")}

    response = client.post("/api/v1/classify", files=files)

    assert response.status_code == 200
    data = response.json()

    # Validamos el nuevo esquema de respuesta
    assert "category" in data
    assert isinstance(data["category"], str)
    assert "confidence" in data
    assert isinstance(data["confidence"], float)

def test_similarity_endpoint_txt():
    files = [
        ("file1", ("doc1.txt", b"El perro corre en el parque.", "text/plain")),
        ("file2", ("doc2.txt", b"El canino juega en el jardin.", "text/plain"))
    ]

    response = client.post("/api/v1/similarity", files=files)

    assert response.status_code == 200
    data = response.json()

    # Validamos el nuevo esquema de respuesta
    assert "similarity" in data
    assert isinstance(data["similarity"], float)
    assert 0.0 <= data["similarity"] <= 1.0

    assert "is_duplicate" in data
    assert isinstance(data["is_duplicate"], bool)

def test_similarity_is_duplicate_logic():
    # Enviamos el mismo texto para forzar alta similitud
    text = b"Texto identico para prueba de duplicidad."
    files = [
        ("file1", ("doc1.txt", text, "text/plain")),
        ("file2", ("doc2.txt", text, "text/plain"))
    ]

    response = client.post("/api/v1/similarity", files=files)
    data = response.json()

    # Debería ser muy cercano a 1.0 y marcado como duplicado
    assert data["similarity"] > 0.90
    assert data["is_duplicate"] is True

def test_empty_file():
    files = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 400
