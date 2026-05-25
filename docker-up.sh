#!/bin/bash

# 🐳 Script de Inicialização - KALI-CORE V3.0 Docker Compose
# Este script inicia a aplicação completa (backend + frontend) usando Docker Compose

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "════════════════════════════════════════════════════════════════"
echo "🐳 KALI-CORE V3.0 - Docker Compose Startup"
echo "════════════════════════════════════════════════════════════════"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}1️⃣  Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker disponível${NC}"

echo ""
echo -e "${BLUE}2️⃣  Parando containers anteriores (se houver)...${NC}"
docker-compose down 2>/dev/null || true
sleep 1

echo ""
echo -e "${BLUE}3️⃣  Iniciando containers (Backend + Frontend)...${NC}"
docker-compose up -d

echo ""
echo -e "${BLUE}4️⃣  Aguardando serviços iniciarem...${NC}"
sleep 5

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Aplicação iniciada com sucesso!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}📍 Endpoints disponíveis:${NC}"
echo -e "  🌐 Frontend  (Vite):    ${BLUE}http://localhost:5190${NC}"
echo -e "  🔌 Backend   (FastAPI): ${BLUE}http://localhost:8001${NC}"
echo -e "  📚 API Docs (Swagger):  ${BLUE}http://localhost:8001/docs${NC}"
echo ""
echo -e "${YELLOW}💡 Comandos úteis:${NC}"
echo "  docker-compose logs -f             # Ver logs em tempo real"
echo "  docker-compose down                # Parar containers"
echo "  docker-compose ps                  # Status dos containers"
echo ""
