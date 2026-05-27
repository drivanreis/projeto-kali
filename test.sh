#!/bin/bash

# ===========================================================================
# Script de Testes - Sistema de Bingo Comunitário
# ===========================================================================
# Plataforma: Linux
# Descrição: Valida se o sistema está funcionando corretamente
# Uso: ./test.sh [--coverage]

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
RUN_COVERAGE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --coverage|-c)
            RUN_COVERAGE=true
            ;;
        -h|--help)
            echo "Uso: ./test.sh [--coverage]"
            echo
            echo "Opções:"
            echo "  --coverage, -c   Executa cobertura backend e frontend após os testes de saúde"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida: $1${NC}"
            echo "Use ./test.sh --help"
            exit 1
            ;;
    esac
    shift
done

echo -e "${BLUE}"
echo "=================================================================="
echo "🧪 KALI-CORE V3 - TESTES DE INTEGRIDADE"
echo "=================================================================="
echo -e "${NC}"

# ===========================================================================
# FUNÇÃO AUXILIAR PARA TESTES
# ===========================================================================

test_url() {
    local url=$1
    local description=$2
    local expected_status=$3
    
    echo -n "   ⏳ ${description}... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ OK (HTTP ${response})${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FALHOU (HTTP ${response}, esperado ${expected_status})${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_container() {
    local container=$1
    local description=$2
    
    echo -n "   ⏳ ${description}... "
    
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "${GREEN}✓ Rodando${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ Não encontrado${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# ===========================================================================
# TESTE 1: VERIFICAÇÃO DE FERRAMENTAS
# ===========================================================================

echo ""
echo -e "${YELLOW}[1/5] Verificando ferramentas necessárias...${NC}"

# Desativa temporariamente para checagem de ferramentas
set +e

echo -n "   ⏳ Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Instalado${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não instalado${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ Docker Compose... "
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ Instalado${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não instalado${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ Node.js... "
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Instalado ($(node --version))${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não instalado${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ curl... "
if command -v curl &> /dev/null; then
    echo -e "${GREEN}✓ Instalado${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não instalado${NC}"
    ((TESTS_FAILED++))
fi

# Reativa o modo estrito para o resto do script
set -e

# ===========================================================================
# TESTE 2: ESTRUTURA DE ARQUIVOS
# ===========================================================================

echo ""
echo -e "${YELLOW}[2/5] Verificando estrutura de arquivos...${NC}"

echo -n "   ⏳ docker compose.yml... "
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓ Existe${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não encontrado${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ backend/Dockerfile... "
if [ -f "backend/Dockerfile" ]; then
    echo -e "${GREEN}✓ Existe${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não encontrado${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ frontend/Dockerfile... "
if [ -f "frontend/Dockerfile" ]; then
    echo -e "${GREEN}✓ Existe${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não encontrado${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ frontend/node_modules... "
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓ Instalado${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não instalado (execute ./install.sh)${NC}"
    ((TESTS_FAILED++))
fi

echo -n "   ⏳ frontend/.env... "
if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓ Existe${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Não encontrado (execute ./install.sh)${NC}"
    ((TESTS_FAILED++))
fi

# ===========================================================================
# TESTE 3: CONTAINERS DOCKER
# ===========================================================================

echo ""
echo -e "${YELLOW}[3/5] Verificando containers Docker...${NC}"

test_container "kali-core-backend" "Container Backend"
test_container "kali-core-frontend" "Container Frontend"

# ===========================================================================
# TESTE 4: ENDPOINTS DO BACKEND
# ===========================================================================

echo ""
echo -e "${YELLOW}[4/5] Testando endpoints do backend...${NC}"

test_url "http://localhost:8001/api/targets" "Healthcheck /api/targets" "200"
test_url "http://localhost:8001/docs" "Documentação Swagger" "200"
test_url "http://localhost:8001/openapi.json" "OpenAPI Schema" "200"

# ===========================================================================
# TESTE 5: FRONTEND
# ===========================================================================

echo ""
echo -e "${YELLOW}[5/5] Testando frontend...${NC}"

test_url "http://localhost:5190" "Frontend (Vite)" "200"

# ===========================================================================
# TESTE FUNCIONAL: PYTEST BACKEND
# ===========================================================================

echo ""
echo -e "${YELLOW}[BONUS] Executando testes unitários (pytest)...${NC}"

echo -n "   ⏳ pytest backend... "

if docker exec kali-core-backend python -m pytest -q 2>/dev/null; then
    echo -e "${GREEN}✓ Testes passaram${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Alguns testes falharam${NC}"
    ((TESTS_FAILED++))
fi

# ===========================================================================
# RESUMO DOS TESTES
# ===========================================================================

echo ""
echo -e "${BLUE}"
echo "=================================================================="
echo "📊 RESUMO DOS TESTES"
echo "=================================================================="
echo -e "${NC}"
echo ""
echo -e "   ✅ Testes aprovados: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "   ❌ Testes falhados:  ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "🎉 TODOS OS TESTES PASSARAM!"
    echo "=================================================================="
    echo -e "${NC}"
    echo ""
    echo "   O sistema está funcionando corretamente!"
    echo ""
    echo "   Acesse:"
    echo "   • Frontend: ${GREEN}http://localhost:5190${NC}"
    echo "   • Backend:  ${GREEN}http://localhost:8001/docs${NC}"
    echo ""

    if [ "$RUN_COVERAGE" = true ]; then
        echo -e "${YELLOW}📈 Executando cobertura backend...${NC}"
        echo ""

        if ! docker ps --format '{{.Names}}' | grep -q '^kali-core-backend$'; then
            echo -e "${RED}❌ Container kali-core-backend não está rodando para cobertura${NC}"
            exit 1
        fi

        echo "   ⏳ Cobertura backend (pytest)..."
        docker exec kali-core-backend python -m pytest --cov=core --cov-report=term

        echo ""
        echo -e "${GREEN}✅ Cobertura concluída${NC}"
        echo ""
    fi

    exit 0
else
    echo -e "${RED}"
    echo "=================================================================="
    echo "⚠️  ALGUNS TESTES FALHARAM"
    echo "=================================================================="
    echo -e "${NC}"
    echo ""
    echo "   Verifique os erros acima e:"
    echo "   1. Certifique-se de que executou: ${YELLOW}./install.sh${NC}"
    echo "   2. Certifique-se de que o sistema está rodando: ${YELLOW}docker compose up${NC}"
    echo "   3. Aguarde alguns segundos para os containers iniciarem"
    echo ""
    exit 1
fi
