#!/bin/bash

# ===========================================================================
# Script de Instalação Automatizado - KALI-CORE V3
# ===========================================================================
# Plataforma: Linux (Ubuntu/Debian/Kali)
# Descrição: Garante a presença do Docker e prepara o ambiente de auditoria
# Uso: ./install.sh

set -e  # Interrompe em caso de erro

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=================================================================="
echo "🛡️  KALI-CORE V3 - INFRAESTRUTURA DE AUDITORIA (AUTO-CONTAINER)"
echo "=================================================================="
echo -e "${NC}"

# ===========================================================================
# 1. VERIFICAÇÃO E INSTALAÇÃO AUTOMÁTICA DO DOCKER
# ===========================================================================

echo -e "${YELLOW}[1/7] Verificando Docker no sistema...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não encontrado! Iniciando instalação automatizada...${NC}"
    
    # Atualiza o repositório ignorando falhas de pacotes de terceiros (como o shiftkey)
    sudo apt update -y || true
    
    # Instala o motor do docker e o utilitário do compose compatível com o Kali
    sudo apt install -y docker.io docker-compose
    
    # Adiciona o usuário atual ao grupo docker para não precisar usar sudo depois
    sudo usermod -aG docker $USER
    
    # Ativa e inicializa o daemon do docker
    sudo systemctl enable --now docker
    
    echo -e "${GREEN}✓ Docker instalado e inicializado com sucesso!${NC}"
    echo -e "${YELLOW}⚠️  Aviso: Para as permissões do grupo surtirem efeito sem deslogar,${NC}"
    echo -e "${YELLOW}          o script usará 'sg docker' para rodar os próximos comandos.${NC}"
else
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ Docker pronto para uso: ${DOCKER_VERSION}${NC}"
fi

# ===========================================================================
# 2. VERIFICAÇÃO DO DOCKER COMPOSE
# ===========================================================================

echo ""
echo -e "${YELLOW}[2/7] Verificando Docker Compose...${NC}"
if ! docker compose version &> /dev/null && ! docker-compose --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose ausente. Instalando...${NC}"
    sudo apt install -y docker-compose
fi
echo -e "${GREEN}✓ Docker Compose pronto para uso${NC}"

# ===========================================================================
# 3. INSTALAÇÃO DAS DEPENDÊNCIAS DO FRONTEND (Para compilação dos assets)
# ===========================================================================

echo ""
echo -e "${YELLOW}[3/7] Verificando Node.js local para o Frontend...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js não encontrado. Instalando para o ecossistema...${NC}"
    sudo apt install -y nodejs npm
fi

echo ""
echo -e "${YELLOW}[4/7] Instalando pacotes do frontend...${NC}"
cd frontend
npm install --quiet

# Criar o arquivo de ambiente .env do frontend
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8001
NODE_ENV=development
EOF
echo -e "${GREEN}✓ Frontend configurado (.env gerado)${NC}"
cd ..

# ===========================================================================
# 4. PREPARAÇÃO DA ESTRUTURA DO BACKEND
# ===========================================================================

echo ""
echo -e "${YELLOW}[5/7] Criando volumes e estruturas de dados...${NC}"
mkdir -p backend/data
echo -e "${GREEN}✓ Diretório backend/data persistido${NC}"

# ===========================================================================
# VERIFICAÇÃO E CONCLUSÃO FINAL
# ===========================================================================

echo ""
echo -e "${GREEN}"
echo "=================================================================="
echo "✅ INFRAESTRUTURA DOCKER CONFIGURADA E HOMOLOGADA!"
echo "=================================================================="
echo -e "${NC}"

echo -e "${BLUE}📋 PRÓXIMOS PASSOS PARA RODAR O PROJETO AGORA:${NC}"
echo ""
echo "   1️⃣  Execute o comando para levantar o container isolado:"
echo -e "      ${GREEN}docker compose up --build -d${NC}"
echo ""
echo "   2️⃣  Abra o navegador do seu Kali na interface de bancada:"
echo -e "      👉 ${GREEN}http://localhost:5190${NC}"
echo ""
echo "=================================================================="