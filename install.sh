#!/bin/bash

# ===========================================================================
# Script de Instalação - Sistema de Bingo Comunitário
# ===========================================================================
# Plataforma: Linux (Ubuntu/Debian)
# Descrição: Prepara o ambiente para primeira execução
# Uso: ./install.sh

set -e  # Para em caso de erro

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=================================================================="
echo "🛡️  KALI-CORE V3 - INFRAESTRUTURA DE AUDITORIA"
echo "=================================================================="
echo -e "${NC}"

# ===========================================================================
# VERIFICAÇÕES DE PRÉ-REQUISITOS
# ===========================================================================

echo -e "${YELLOW}[1/7] Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado!${NC}"
    echo "   Instale o Docker: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi
DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓ Docker instalado: ${DOCKER_VERSION}${NC}"

echo ""
echo -e "${YELLOW}[2/7] Verificando Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado!${NC}"
    echo "   Docker Compose v2 é necessário"
    exit 1
fi
COMPOSE_VERSION=$(docker compose version)
echo -e "${GREEN}✓ Docker Compose instalado: ${COMPOSE_VERSION}${NC}"

echo ""
echo -e "${YELLOW}[3/7] Verificando Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado!${NC}"
    echo "   Instale o Node.js 18+: https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js instalado: ${NODE_VERSION}${NC}"

echo ""
echo -e "${YELLOW}[4/7] Verificando npm...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm não encontrado!${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm instalado: ${NPM_VERSION}${NC}"

# ===========================================================================
# INSTALAÇÃO DAS DEPENDÊNCIAS DO BACKEND (NO CONTÊINER)
# ===========================================================================

echo ""
echo -e "${YELLOW}[5/7] Instalando dependências Python no contêiner backend...${NC}"

if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}❌ Arquivo backend/requirements.txt não encontrado!${NC}"
    exit 1
fi

echo "   Executando pip install -r requirements.txt no Python global do contêiner..."
docker compose run --rm backend pip install --no-cache-dir -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependências do backend instaladas no contêiner${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências do backend${NC}"
    exit 1
fi

# ===========================================================================
# INSTALAÇÃO DAS DEPENDÊNCIAS DO FRONTEND
# ===========================================================================

echo ""
echo -e "${YELLOW}[6/7] Instalando dependências do frontend...${NC}"
cd frontend

if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Arquivo package.json não encontrado!${NC}"
    exit 1
fi

echo "   Executando npm install..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependências do frontend instaladas com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências${NC}"
    exit 1
fi

# ===========================================================================
# CRIAÇÃO DO ARQUIVO .env
# ===========================================================================

echo ""
echo -e "${YELLOW}[7/7] Criando arquivo .env do frontend...${NC}"

if [ -f ".env" ]; then
    echo "   Arquivo .env já existe, fazendo backup..."
    cp .env .env.backup
    echo -e "${GREEN}✓ Backup criado: .env.backup${NC}"
fi

cat > .env << 'EOF'
# ===========================================================================
# Variáveis de Ambiente - Frontend KALI-CORE V3
# ===========================================================================
# Gerado automaticamente pelo install.sh

# URL do Backend
VITE_API_URL=http://localhost:8001

# Ambiente
NODE_ENV=development

# ===========================================================================
# INSTRUÇÕES:
# - Em produção, altere VITE_API_URL para o domínio real da API
# - Não commitar este arquivo com credenciais sensíveis
# ===========================================================================
EOF

echo -e "${GREEN}✓ Arquivo .env criado com sucesso${NC}"

cd ..

# ===========================================================================
# PREPARAÇÃO DO DIRETÓRIO DE DADOS
# ===========================================================================

echo ""
echo -e "${YELLOW}Preparando diretório de dados do backend...${NC}"

if [ ! -d "backend/data" ]; then
    mkdir -p backend/data
    echo -e "${GREEN}✓ Diretório backend/data criado${NC}"
else
    echo -e "${GREEN}✓ Diretório backend/data já existe${NC}"
fi

# ===========================================================================
# VERIFICAÇÃO FINAL
# ===========================================================================

echo ""
echo -e "${GREEN}"
echo "=================================================================="
echo "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=================================================================="
echo -e "${NC}"

echo ""
echo -e "${BLUE}📋 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "   1️⃣  Inicie o sistema completo:"
echo "      ${GREEN}docker compose up --build${NC}"
echo ""
echo "   2️⃣  Acesse no navegador:"
echo "      Frontend:  ${GREEN}http://localhost:5190${NC}"
echo "      Backend:   ${GREEN}http://localhost:8001${NC}"
echo "      Docs API:  ${GREEN}http://localhost:8001/docs${NC}"
echo ""
echo "   3️⃣  Acesso ao Dashboard:"
echo "      Fluxo: ${GREEN}/${NC} (Acesso direto ao Dashboard do Analista)"
echo "      Banco: ${GREEN}SQLite em backend/data/attack_history.db${NC}"
echo ""
echo -e "${YELLOW}💡 Dica: Use './start.sh' para iniciar o sistema rapidamente${NC}"
echo ""
echo "=================================================================="
