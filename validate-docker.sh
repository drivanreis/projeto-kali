#!/bin/bash

# 🐳 Script de Validação Docker - KALI-CORE V3.0
# Este script valida a configuração Docker antes de fazer o build completo

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🐳 KALI-CORE V3.0 - Docker Validation"
echo "════════════════════════════════════════════════════════════════"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_tool() {
    local tool=$1
    if command -v $tool &> /dev/null; then
        echo -e "${GREEN}✅${NC} $tool está instalado: $(which $tool)"
    else
        echo -e "${RED}❌${NC} $tool NÃO está instalado"
        exit 1
    fi
}

echo ""
echo "1️⃣  Verificando ferramentas necessárias..."
echo "───────────────────────────────────────"
check_tool docker
check_tool docker-compose

echo ""
echo "2️⃣  Verificando versões..."
echo "───────────────────────────────────────"
DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
NODE_VERSION=$(grep -oP '"version": "\K[^"]+' package.json)

echo -e "${GREEN}✅${NC} Docker: $DOCKER_VERSION"
echo -e "${GREEN}✅${NC} Docker Compose: $COMPOSE_VERSION"
echo -e "${GREEN}✅${NC} Projeto: KALI-CORE V3.0"

echo ""
echo "3️⃣  Verificando arquivos necessários..."
echo "───────────────────────────────────────"

files_to_check=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    ".dockerignore"
    "package.json"
    "backend/requirements.txt"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file existe"
    else
        echo -e "${RED}❌${NC} $file está faltando"
        exit 1
    fi
done

echo ""
echo "4️⃣  Validando docker-compose.yml..."
echo "───────────────────────────────────────"
if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} docker-compose.yml é válido"
else
    echo -e "${RED}❌${NC} docker-compose.yml tem erros"
    docker-compose config
    exit 1
fi

echo ""
echo "5️⃣  Verificando conectividade Docker..."
echo "───────────────────────────────────────"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Docker daemon está rodando"
else
    echo -e "${RED}❌${NC} Docker daemon não está respondendo"
    exit 1
fi

echo ""
echo "6️⃣  Validando Dockerfiles..."
echo "───────────────────────────────────────"

# Verificar backend Dockerfile
echo "Verificando backend/Dockerfile..."
if grep -q "FROM python:3.11-slim" backend/Dockerfile && \
   grep -q "EXPOSE 8001" backend/Dockerfile && \
   grep -q "HEALTHCHECK" backend/Dockerfile; then
    echo -e "${GREEN}✅${NC} backend/Dockerfile contém elementos necessários"
else
    echo -e "${RED}❌${NC} backend/Dockerfile está incompleto"
    exit 1
fi

# Verificar frontend Dockerfile
echo "Verificando frontend/Dockerfile..."
if grep -q "FROM node:18-alpine" frontend/Dockerfile && \
   grep -q "EXPOSE 5190" frontend/Dockerfile; then
    echo -e "${GREEN}✅${NC} frontend/Dockerfile contém elementos necessários"
else
    echo -e "${RED}❌${NC} frontend/Dockerfile está incompleto"
    exit 1
fi

echo ""
echo "7️⃣  Estimativa de espaço em disco..."
echo "───────────────────────────────────────"
available_space=$(df -h . | tail -1 | awk '{print $4}')
echo -e "Espaço disponível: ${YELLOW}$available_space${NC}"
echo "Espaço estimado para imagens: ~400MB (backend 150MB + frontend 170MB + deps)"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ VALIDAÇÃO COMPLETA - Tudo pronto para build!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Para iniciar os containers, execute:"
echo -e "${YELLOW}docker compose up --build${NC}"
echo ""
echo "Acessar:"
echo -e "  Frontend: ${YELLOW}http://localhost:5190${NC}"
echo -e "  Backend:  ${YELLOW}http://localhost:8001${NC}"
echo -e "  API Docs: ${YELLOW}http://localhost:8001/docs${NC}"
echo ""
