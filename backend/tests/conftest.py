"""
Configuração do pytest para KALI-CORE V3 Backend
"""
import sys
import os

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Variáveis de ambiente para testes
os.environ['TESTING'] = 'true'
