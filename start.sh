#!/bin/bash
# ===========================================================================
# Script de Inicialização - KALI-CORE V3
# ===========================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}🚀 INICIANDO ECOSSISTEMA KALI-CORE V3 (DOCKER)${NC}"
echo -e "${BLUE}==================================================================${NC}"

# Sobe os containers orquestrados em segundo plano reconstruindo se necessário
docker compose up --build -d

echo ""
echo -e "${GREEN}✅ SISTEMA SUBIU COM SUCESSO!${NC}"
echo ""
echo -e "${BLUE}🔒 ECOSSISTEMA ADMINISTRATIVO (ESCONDIDO/LOCAL):${NC}"
echo -e "   painel do auditor:   ${GREEN}http://localhost:3000${NC}"
echo -e "   api administrativa:  ${GREEN}http://localhost:5190${NC}"
echo -e "   docs api interna:    ${GREEN}http://localhost:5190/docs${NC}"
echo ""
echo -e "${YELLOW}🌐 PORTAL PÚBLICO EXPOSTO (MÁQUINAS CLIENTES):${NC}"
echo -e "   portaria de coleta:  ${GREEN}http://<IP_DO_SERVIDOR>:8888/audit${NC}"
echo ""
echo -e "${BLUE}💡 Dica: Se algo falhar, use './limpa.sh' para resetar ou './test.sh' para testar.${NC}"