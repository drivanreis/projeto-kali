# 🚀 KALI-CORE V3.0 - Docker Quick Start Guide

## ⚡ 5 Minutos para Rodar

### Pré-requisitos
- Docker 20.10+
- Docker Compose 2.0+
- ~600MB de espaço em disco

### Step 1: Validar Setup
```bash
chmod +x validate-docker.sh
./validate-docker.sh
```

Você verá:
- ✅ Docker daemon rodando
- ✅ Dockerfiles validados
- ✅ docker-compose.yml válido
- ✅ Espaço em disco suficiente

### Step 2: Build e Iniciar
```bash
docker compose up --build
```

Você verá:
```
kali-core-backend    | INFO:     Application startup complete
kali_frontend        | VITE v5.0.8 ready in XXX ms
```

### Step 3: Acessar Aplicação
- **Frontend:** http://localhost:5190
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs (Swagger)

### Step 4: Testar
1. Insira IP/domínio em "INJEÇÃO SUTIL"
2. Selecione táticas
3. Clique "[ INICIAR OPERAÇÃO ]"
4. Acesse "[ AUDITORIA ]"
5. Gere "[ RELATÓRIO ]"

---

## 🛑 Parar Containers

### Background
```bash
docker compose down
```

### Com cleanup de volumes
```bash
docker compose down -v
```

---

## 📊 Monitorar

### Ver status
```bash
docker compose ps
```

Output:
```
NAME                 IMAGE              STATUS
kali-core-backend    kali-core:backend  Up (healthy)
kali-core-frontend   kali-core:frontend Up
```

### Ver logs
```bash
docker compose logs -f                    # Todos
docker compose logs -f kali_backend       # Só backend
docker compose logs -f kali_frontend      # Só frontend
```

### Health check
```bash
docker compose inspect kali-core-backend | grep -A 10 "Health"
```

---

## 🔧 Desenvolvimento (Hot-Reload)

### Arquivo alterado em src/
```bash
# Vite detecta mudança automaticamente
# Navegador faz refresh em ~1s
# Container continua rodando
```

### Backend (Adicionar --reload)
Edit `docker-compose.yml`:
```yaml
kali_backend:
  environment:
    - DEVELOPMENT=true
```

Depois altere o CMD em `backend/Dockerfile`:
```dockerfile
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

Rebuild:
```bash
docker compose up --build kali_backend
```

---

## 🐛 Troubleshooting

### "Port 5190 already in use"
```bash
# Opção 1: Usar porta diferente
docker compose -f docker-compose.yml -p alternative up --build

# Opção 2: Matar processo na porta
lsof -i :5190
kill -9 <PID>
```

### "kali_backend is unhealthy"
```bash
docker compose logs kali_backend
# Verifique se /api/targets está respondendo
curl http://localhost:8001/api/targets
```

### "Cannot reach backend from frontend"
```bash
# Verificar network
docker network ls
docker network inspect kali-network

# Executar curl dentro do frontend container
docker compose exec kali_frontend curl http://kali_backend:8001/api/targets
```

### "npm install failed"
```bash
# Limpar e rebuildar
docker compose down -v
docker compose up --build
```

### Limpar TUDO
```bash
docker compose down -v
docker system prune -a
docker volume prune
# Depois: docker compose up --build
```

---

## 📁 Estrutura de Dados

### Onde os dados são armazenados?
```bash
# Banco de dados
./backend/data/attack_history.db

# Logs de aplicação
docker compose logs kali_backend
```

### Fazer backup do database
```bash
cp backend/data/attack_history.db backend/data/attack_history.db.backup
```

### Restaurar backup
```bash
cp backend/data/attack_history.db.backup backend/data/attack_history.db
docker compose restart kali_backend
```

---

## 🌐 Networking

### Acessar de outra máquina
```bash
# Altere docker-compose.yml:
# "5190:5190" → "0.0.0.0:5190:5190"
# "8001:8001" → "0.0.0.0:8001:8001"

# Depois acesse:
# http://<seu-ip>:5190
# http://<seu-ip>:8001
```

### Hostname dentro do Docker
```bash
# Frontend pode acessar backend via:
http://kali_backend:8001  # (não localhost!)
```

---

## 🚢 Deploy para Produção

### Step 1: Criar .env.production
```bash
cp .env.docker.example .env.production
```

Edit e altere:
```env
ENVIRONMENT=production
DEBUG=False
NODE_ENV=production
```

### Step 2: Build otimizado
```bash
# Remover volumes de desenvolvimento
# Remover --reload do backend
# Frontend usar npm run build
```

### Step 3: Run com restart policy
```yaml
services:
  kali_backend:
    restart: always
  kali_frontend:
    restart: always
```

### Step 4: Iniciar
```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 📋 Checklist Final

- [ ] Docker e Docker Compose instalados
- [ ] ./validate-docker.sh passou
- [ ] docker compose up --build completou
- [ ] Frontend acessível em :5190
- [ ] Backend respondendo em :8001
- [ ] Healthcheck OK
- [ ] Injeção sutil → operação → auditoria funciona
- [ ] Logs sem erros críticos

---

## 🎯 Próximas Etapas

1. ✅ Containers rodando localmente
2. ⏭️ Configurar CI/CD (GitHub Actions)
3. ⏭️ Deploy em staging
4. ⏭️ Deploy em produção

---

## 📞 Comandos Úteis

```bash
# Iniciar em background
docker compose up -d --build

# Parar
docker compose stop

# Reiniciar
docker compose restart

# Ver todas as imagens
docker images | grep kali

# Inspecionar container
docker inspect kali-core-backend

# Acessar shell do backend
docker compose exec kali_backend bash

# Acessar shell do frontend
docker compose exec kali_frontend sh

# Remover container específico
docker compose rm kali_backend

# Ver resource usage
docker stats

# Push para registry (future)
docker tag kali-core-backend:latest myregistry/kali-core-backend:latest
docker push myregistry/kali-core-backend:latest
```

---

## 🔐 Segurança

- ✅ Imagens baseadas em versões oficiais
- ✅ Python slim (reduz surface)
- ✅ Node alpine (reduz surface)
- ✅ Healthcheck monitora disponibilidade
- ✅ Network isolado (kali-network)
- ⚠️ TODO: Secrets management (produção)
- ⚠️ TODO: HTTPS/TLS (produção)

---

**Status:** ✅ PRONTO PARA USAR  
**Versão:** Docker Compose 3.8  
**Tempo de Setup:** ~5 minutos  
**Tempo de Deploy:** ~2 minutos

Bom coding! 🎯
