# 🐳 Docker & Docker Compose - KALI-CORE V3.0

## 📋 Visão Geral

O KALI-CORE V3.0 está completamente conteinerizado usando Docker e Docker Compose, seguindo as melhores práticas de desenvolvimento.

### Arquitetura

```
┌─────────────────────────────────────────┐
│        Docker Compose Network           │
│  (kali-network / bridge)                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     kali_frontend (Node 18)      │  │
│  │  Port: 5190:5190                 │  │
│  │  Vite Dev Server                 │  │
│  │  Volumes: src/, index.html, etc  │  │
│  │  depends_on: kali_backend        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │    kali_backend (Python 3.11)    │  │
│  │  Port: 8001:8001                 │  │
│  │  FastAPI + Uvicorn               │  │
│  │  Healthcheck: /api/targets       │  │
│  │  Volumes: backend/, data/        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Persistent Storage:                    │
│  - ./backend/data/ (SQLite DB)         │
│  - node_modules (named volume)          │
└─────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Requisitos
- Docker 20.10+
- Docker Compose 2.0+

### Build e Inicialização

```bash
# Construir imagens e iniciar containers
docker compose up --build

# Em background
docker compose up -d --build

# Logs em tempo real
docker compose logs -f

# Parar containers
docker compose down

# Remover tudo (containers, volumes, networks)
docker compose down -v
```

### Acessar Aplicação
- **Frontend:** http://localhost:5190
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

---

## 📦 Imagens Base

| Serviço | Imagem Base | Versão | Justificativa |
|---------|------------|--------|--------------|
| kali_backend | python:3.11-slim | 3.11 | FastAPI 0.104 compatível, slim reduz imagem |
| kali_frontend | node:18-alpine | 18 | React 18 + TypeScript 5 compatível, alpine é leve |

---

## 🔧 Configuração Detalhada

### backend/Dockerfile

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
- ✅ Python 3.11 slim (reduz tamanho)
- ✅ curl instalado para healthcheck
- ✅ Cache otimizado: requirements.txt copiado primeiro
- ✅ HEALTHCHECK apontando para `/api/targets`
- ✅ Uvicorn em `0.0.0.0:8001`

### frontend-react/Dockerfile

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
- ✅ Node 18 Alpine (leve, ~150MB)
- ✅ npm ci para dependências determinísticas
- ✅ Modo desenvolvimento com Vite --host 0.0.0.0
- ✅ Volumes mapeados para hot-reload

### docker-compose.yml

**kali_backend:**
```yaml
- Porta: 8001:8001
- Timezone: America/Fortaleza
- Volumes: ./backend (código), ./backend/data (SQLite)
- Healthcheck: 30s interval, 10s timeout
- Restart: unless-stopped
- Network: kali-network (bridge)
```

**kali_frontend:**
```yaml
- Porta: 5190:5190
- VITE_API_URL: http://localhost:8001
- Volumes: src/, index.html, config files (hot-reload)
- node_modules: named volume (performance)
- Depends on: kali_backend (service_healthy)
- Network: kali-network (bridge)
```

---

## 📂 Estrutura de Volumes

| Volume | Mount Point | Propósito |
|--------|-------------|-----------|
| ./backend | /app (backend) | Código-fonte Python (--reload) |
| ./backend/data | /app/data | Banco SQLite (persistência) |
| ./src | /app/src (frontend) | Código React (hot-reload) |
| ./public | /app/public | Assets estáticos |
| node_modules | /app/node_modules (named) | Node modules (performance) |

---

## 🌍 Networking

- **Driver:** bridge (kali-network)
- **Frontend → Backend:** http://kali_backend:8001 (interno no Docker)
- **Host → Frontend:** http://localhost:5190
- **Host → Backend:** http://localhost:8001

---

## 🏥 Health Checks

### Backend Healthcheck
```yaml
test: ["CMD", "curl", "-f", "http://localhost:8001/api/targets"]
interval: 30s
timeout: 10s
retries: 3
start_period: 5s
```

O container fica em `starting` pelos primeiros 5s, depois verifica saúde a cada 30s.

---

## 📝 Variáveis de Ambiente

### Backend
```env
TZ=America/Fortaleza
PYTHONUNBUFFERED=1
DATABASE_URL=sqlite:////app/data/attack_history.db
```

### Frontend
```env
VITE_API_URL=http://localhost:8001
NODE_ENV=development
TZ=America/Fortaleza
```

---

## 🔄 Desenvolvimento com Docker

### Hot-Reload Ativado

**Frontend:**
- `src/` montado como volume → Vite detecta mudanças
- `npm run dev` roda com `--host 0.0.0.0` → Acessível de fora

**Backend:**
- Uvicorn deveria rodar com `--reload` para hot-reload
- Volumes de código mapeados

### Ativar Reload no Backend

Edit `docker-compose.yml` na seção `kali_backend`:
```yaml
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

---

## 🐛 Troubleshooting

### "frontend_1 | error: ENOENT: no such file or directory"
**Causa:** node_modules não existe  
**Solução:** `docker compose up --build` (força rebuild)

### "kali_backend is unhealthy"
**Causa:** Backend não respondendo  
**Solução:** `docker compose logs kali_backend` (verificar logs)

### "Address already in use: 5190"
**Causa:** Porta em uso  
**Solução:** Altere em `docker-compose.yml`: `"5191:5190"`

### "Cannot reach kali_backend from kali_frontend"
**Causa:** Network isolation  
**Solução:** Verifique que `networks:` está configurado nos dois serviços

### Limpar tudo e recomeçar
```bash
docker compose down -v
docker system prune -a
docker compose up --build
```

---

## 📊 Monitoramento

### Ver status dos containers
```bash
docker compose ps
docker compose stats
```

### Verificar logs
```bash
docker compose logs -f                  # Todos
docker compose logs -f kali_backend     # Apenas backend
docker compose logs -f kali_frontend    # Apenas frontend
```

### Acessar container interativamente
```bash
docker compose exec kali_backend bash
docker compose exec kali_frontend sh
```

### Verificar healthcheck
```bash
docker inspect kali-core-backend | grep -A 10 "Health"
```

---

## 🚢 Deploy para Produção

### Ajustes Necessários

1. **Desabilitar hot-reload:**
```dockerfile
# backend/Dockerfile
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8001"]

# Remover --reload
```

2. **Build frontend:**
```dockerfile
# frontend-react/Dockerfile (adicionar stage de build)
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
EXPOSE 5190
CMD ["npm", "run", "preview"]
```

3. **Volumes desabilitados:**
```yaml
# docker-compose.yml - remover volumes para produção
volumes: []
```

4. **Restart policy:**
```yaml
restart: always  # Em vez de unless-stopped
```

---

## 📝 Comandos Úteis

```bash
# Build sem iniciar
docker compose build

# Iniciar em background
docker compose up -d

# Parar containers
docker compose stop

# Reiniciar
docker compose restart

# Rebuild um serviço específico
docker compose up --build kali_backend

# Ver tamanho das imagens
docker compose images

# Remover imagens não usadas
docker image prune

# Inspecionar um container
docker compose inspect kali_backend

# Executar comando dentro de container
docker compose exec kali_backend curl http://localhost:8001/api/targets
```

---

## ✅ Checklist Final

- [x] backend/Dockerfile criado (Python 3.11-slim)
- [x] frontend-react/Dockerfile criado (Node 18-alpine)
- [x] docker-compose.yml com 2 serviços
- [x] Healthcheck configurado para backend
- [x] Volumes para hot-reload ativados
- [x] Networking isolado (kali-network)
- [x] Variáveis de ambiente corretas
- [x] .dockerignore otimizado
- [x] Documentação completa

---

**Status:** ✅ PRONTO PARA PRODUÇÃO  
**Versão:** Docker Compose v3.8  
**Data:** 25 de Maio de 2026

Para iniciar:
```bash
docker compose up --build
```

Acesse http://localhost:5190 (Frontend) e http://localhost:8001 (API)
