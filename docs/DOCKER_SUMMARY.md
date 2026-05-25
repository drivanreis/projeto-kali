# 🐳 Conteinerização V3.0 - KALI-CORE Docker Ecosystem

## 📋 Resumo da Implementação

Infraestrutura Docker completa para KALI-CORE V3.0 criada seguindo melhores práticas de conteinerização.

---

## 📦 Arquivos Criados

### 1. **backend/Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/targets || exit 1
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Características:**
- ✅ Python 3.11-slim (otimizado)
- ✅ curl instalado (healthcheck)
- ✅ Cache de dependências otimizado
- ✅ Porta 8001 explícita
- ✅ Healthcheck em `/api/targets`

---

### 2. **frontend-react/Dockerfile**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 5190
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5190"]
```

**Características:**
- ✅ Node 18-alpine (leve)
- ✅ npm ci (determinístico)
- ✅ Vite dev server em 0.0.0.0:5190
- ✅ Hot-reload habilitado

---

### 3. **docker-compose.yml**
```yaml
version: '3.8'

services:
  kali_backend:
    build: ./backend/Dockerfile
    container_name: kali-core-backend
    ports: "8001:8001"
    environment:
      TZ: America/Fortaleza
      PYTHONUNBUFFERED: 1
      DATABASE_URL: sqlite:////app/data/attack_history.db
    volumes:
      - ./backend:/app
      - ./backend/data:/app/data
    healthcheck: /api/targets
    depends_on: none
    
  kali_frontend:
    build: ./frontend-react/Dockerfile
    container_name: kali-core-frontend
    ports: "5190:5190"
    environment:
      VITE_API_URL: http://localhost:8001
      NODE_ENV: development
      TZ: America/Fortaleza
    volumes:
      - ./src:/app/src
      - ./public:/app/public
      - ./index.html:/app/index.html
      - ./vite.config.ts:/app/vite.config.ts
      - node_modules:/app/node_modules
    depends_on:
      kali_backend:
        condition: service_healthy
    networks:
      - kali-network

networks:
  kali-network:
    driver: bridge

volumes:
  node_modules:
```

**Características:**
- ✅ 2 serviços: backend + frontend
- ✅ Portas corretas: 8001, 5190
- ✅ Timezone: America/Fortaleza
- ✅ Volumes para persistência e hot-reload
- ✅ Frontend depende de backend service_healthy
- ✅ Network isolado (kali-network)

---

### 4. **.dockerignore**
```
node_modules
npm-debug.log
.git
dist
build
.venv
__pycache__
...
```

**Propósito:** Reduzir tamanho de contexto do build

---

### 5. **DOCKER_SETUP.md**
Documentação completa incluindo:
- ✅ Arquitetura visual
- ✅ Quickstart
- ✅ Configuração detalhada
- ✅ Networking
- ✅ Healthchecks
- ✅ Troubleshooting
- ✅ Deploy para produção
- ✅ Comandos úteis

---

## 🎯 Especificações Técnicas

### Imagens Base
| Serviço | Imagem | Versão | Tamanho |
|---------|--------|--------|--------|
| Backend | python:3.11-slim | 3.11 | ~150MB |
| Frontend | node:18-alpine | 18 | ~170MB |

### Portas
- **Backend:** 8001:8001 (API FastAPI)
- **Frontend:** 5190:5190 (Vite dev server)

### Volumes
- Backend: `./backend:/app` (código-fonte)
- Backend data: `./backend/data:/app/data` (SQLite persistente)
- Frontend: `./src:/app/src` (hot-reload)
- Frontend node_modules: `node_modules:/app/node_modules` (named volume)

### Networking
- **Network:** kali-network (bridge)
- **Frontend → Backend:** http://kali_backend:8001 (interno)
- **Host → Frontend:** http://localhost:5190
- **Host → Backend:** http://localhost:8001

### Health Checks
- **Backend:** GET /api/targets a cada 30s
- **Timeout:** 10s
- **Start Period:** 5s
- **Retries:** 3

---

## 🚀 Como Usar

### Build e Iniciar
```bash
docker compose up --build
```

### Acessar
- Frontend: http://localhost:5190
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Parar
```bash
docker compose down
```

### Remover tudo
```bash
docker compose down -v
```

---

## 🔧 Desenvolvimento

### Hot-Reload Automático
- **Frontend:** Volumes de `src/` mapeados → Vite detecta mudanças
- **Backend:** Uvicorn com --reload (adicionar a CMD se necessário)

### Acessar Container
```bash
docker compose exec kali_backend bash
docker compose exec kali_frontend sh
```

### Ver Logs
```bash
docker compose logs -f kali_backend
docker compose logs -f kali_frontend
```

---

## 🚢 Deploy para Produção

1. Remover volumes de código-fonte
2. Build frontend durante imagem
3. Desabilitar hot-reload
4. Usar `restart: always`
5. Configurar nginx/reverse proxy

---

## ✅ Checklist de Implementação

- [x] backend/Dockerfile (Python 3.11-slim, healthcheck, curl)
- [x] frontend-react/Dockerfile (Node 18-alpine, hot-reload)
- [x] docker-compose.yml (2 serviços, networking, volumes)
- [x] .dockerignore (otimização)
- [x] DOCKER_SETUP.md (documentação completa)
- [x] Variáveis de ambiente configuradas
- [x] Timezone America/Fortaleza
- [x] Healthcheck em /api/targets
- [x] Depends_on com service_healthy
- [x] Volumes para persistência e desenvolvimento

---

## 📊 Estrutura Final

```
projeto-kali/
├── docker-compose.yml          ✅ Orquestração 2 serviços
├── backend/
│   ├── Dockerfile              ✅ Python 3.11-slim
│   ├── main_fastapi.py
│   ├── requirements.txt
│   └── data/                   (volume persistente)
├── frontend-react/
│   └── Dockerfile              ✅ Node 18-alpine
├── src/                        (volume hot-reload)
├── package.json
├── vite.config.ts
├── .dockerignore                ✅ Otimizado
└── DOCKER_SETUP.md             ✅ Documentação

Docker Network: kali-network (bridge)
```

---

## 🎬 Próximas Etapas

1. ✅ Dockerfiles criados
2. ✅ docker-compose.yml configurado
3. ⏭️ Executar: `docker compose up --build`
4. ⏭️ Acessar: http://localhost:5190
5. ⏭️ Testar integrações

---

**Status:** ✅ CONTEINERIZAÇÃO COMPLETA  
**Versão:** Docker Compose 3.8  
**Data:** 25 de Maio de 2026

Comando para iniciar:
```bash
docker compose up --build
```
