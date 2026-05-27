#!/bin/bash
# ===========================================================================
# Script de Inicialização - KALI-CORE V3
# ===========================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}🚀 INICIANDO ECOSSISTEMA KALI-CORE V3 (DOCKER)${NC}"
echo -e "${BLUE}==================================================================${NC}"

# Sobe os containers orquestrados em segundo plano reconstruindo se necessário
docker compose up --build -d

echo ""
echo -e "${GREEN}✅ SISTEMA SUBIU COM SUCESSO!${NC}"
echo -e "   Frontend Ativo: ${GREEN}http://localhost:5190${NC}"
echo -e "   Backend Ativo:  ${GREEN}http://localhost:8001${NC}"
echo -e "   Docs API Ativa: ${GREEN}http://localhost:8001/docs${NC}"
echo ""
echo -e "${BLUE}💡 Dica: Se algo falhar, use './limpa.sh' para resetar ou './test.sh' para testar.${NC}"
