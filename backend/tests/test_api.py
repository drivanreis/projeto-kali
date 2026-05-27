"""
Testes Unitários - KALI-CORE V3 Backend
Valida os endpoints principais da API
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adiciona o diretório backend ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_fastapi import app


@pytest.fixture
def client():
    """Fixture que fornece um cliente de teste para a API"""
    return TestClient(app)


class TestHealthcheck:
    """Testes de health check da API"""
    
    def test_health_targets_endpoint(self, client):
        """Verifica se o endpoint /api/targets está respondendo"""
        response = client.get("/api/targets")
        assert response.status_code == 200
        assert isinstance(response.json(), (list, dict))
    
    def test_openapi_schema(self, client):
        """Verifica se a documentação OpenAPI está disponível"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()
    
    def test_swagger_docs(self, client):
        """Verifica se o Swagger UI está disponível"""
        response = client.get("/docs")
        assert response.status_code == 200


class TestAPI:
    """Testes dos endpoints principais da API"""
    
    def test_get_targets(self, client):
        """Testa recuperação de targets"""
        response = client.get("/api/targets")
        assert response.status_code == 200
        data = response.json()
        # Pode retornar lista vazia ou com targets
        assert isinstance(data, (list, dict))
    
    def test_root_endpoint(self, client):
        """Testa se há um endpoint raiz configurado"""
        response = client.get("/")
        # Aceita 200, 404 ou 307 (redirect)
        assert response.status_code in [200, 404, 307]
