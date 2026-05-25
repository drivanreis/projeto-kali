# 📚 KALI-CORE V3.0 - Documentação Centralizada

**Projeto:** KALI-CORE  
**Versão:** 3.0.0  
**Data de Atualização:** 25 de Maio de 2026  
**Status:** ✅ Pronto para Deployment

---

## 🎯 Guia Rápido

### Para Iniciantes
1. **[QUICKSTART_V3.md](QUICKSTART_V3.md)** - Comece aqui! Instruções passo-a-passo para rodar tudo
2. **[README_WEB_DASHBOARD.md](README_WEB_DASHBOARD.md)** - Guia da interface web e como usar o dashboard
3. **[STATUS_FINAL.md](STATUS_FINAL.md)** - Visão geral final do projeto e como iniciar

### Para DevOps / Infra
1. **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Iniciar com Docker Compose em 3 comandos
2. **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Configuração completa do Docker
3. **[DOCKER_SUMMARY.md](DOCKER_SUMMARY.md)** - Resumo técnico da arquitetura Docker

### Para Arquitetura e Estrutura
1. **[PROJECT_MAP.md](PROJECT_MAP.md)** - Mapa completo do projeto, banco de dados, schemas SQL
2. **[KALI_V3_COMPLETE.md](KALI_V3_COMPLETE.md)** - Documentação técnica completa v3.0
3. **[MIGRATION_V3.md](MIGRATION_V3.md)** - Histórico de migração da v2.x para v3.0

### Para CSS e Frontend
1. **[CSS_INTEGRATION_GUIDE.md](CSS_INTEGRATION_GUIDE.md)** - Guia de integração CSS, styling e temas
2. **[README_WEB_DASHBOARD.md](README_WEB_DASHBOARD.md)** - Componentes React e sua estrutura

### Checklist e Limpeza
1. **[HYGIENE_V3_SUMMARY.md](HYGIENE_V3_SUMMARY.md)** - Resumo da higienização (zero legado)
2. **[MIGRATION_V3_CHECKLIST.md](MIGRATION_V3_CHECKLIST.md)** - Checklist final de v2 → v3

---

## 📋 Índice de Documentos

| Documento | Categoria | Descrição |
|-----------|-----------|-----------|
| [QUICKSTART_V3.md](QUICKSTART_V3.md) | 🚀 Início Rápido | Passo-a-passo para rodar a aplicação |
| [STATUS_FINAL.md](STATUS_FINAL.md) | 📊 Status | Estado final do projeto (500+ linhas) |
| [README_WEB_DASHBOARD.md](README_WEB_DASHBOARD.md) | 🌐 Frontend | Guia da interface web e dashboard |
| [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) | 🐳 DevOps | Iniciar Docker em 3 comandos |
| [DOCKER_SETUP.md](DOCKER_SETUP.md) | 🐳 DevOps | Configuração completa Docker |
| [DOCKER_SUMMARY.md](DOCKER_SUMMARY.md) | 🐳 DevOps | Resumo arquitetura Docker |
| [PROJECT_MAP.md](PROJECT_MAP.md) | 🗺️ Arquitetura | Mapa do projeto + DB schemas |
| [KALI_V3_COMPLETE.md](KALI_V3_COMPLETE.md) | 📚 Técnico | Documentação técnica completa |
| [MIGRATION_V3.md](MIGRATION_V3.md) | 🔄 Histórico | Migração v2 → v3 |
| [CSS_INTEGRATION_GUIDE.md](CSS_INTEGRATION_GUIDE.md) | 🎨 Frontend | Guia CSS e styling |
| [HYGIENE_V3_SUMMARY.md](HYGIENE_V3_SUMMARY.md) | 🧹 Limpeza | Higienização e zero legado |
| [MIGRATION_V3_CHECKLIST.md](MIGRATION_V3_CHECKLIST.md) | ✅ Checklist | Checklist final migração |

---

## 🏗️ Estrutura do Projeto

```
projeto-kali/
├── docs/                          # 📚 Documentação centralizada (este índice)
│   ├── index.md                   # ← Você está aqui!
│   ├── QUICKSTART_V3.md
│   ├── STATUS_FINAL.md
│   ├── README_WEB_DASHBOARD.md
│   ├── DOCKER_*.md
│   ├── PROJECT_MAP.md
│   ├── KALI_V3_COMPLETE.md
│   ├── MIGRATION_*.md
│   ├── CSS_INTEGRATION_GUIDE.md
│   └── HYGIENE_V3_SUMMARY.md
│
├── frontend/                      # ⚛️ React + TypeScript + Vite (Porta 5190)
│   ├── Dockerfile
│   ├── src/
│   │   ├── components/            # Componentes React
│   │   ├── context/               # React Context
│   │   ├── styles/                # CSS modular (global.css + componentes)
│   │   ├── types/                 # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── backend/                       # 🔌 FastAPI + Python 3.11 (Porta 8001)
│   ├── Dockerfile
│   ├── main_fastapi.py            # Entry point
│   ├── models.py
│   ├── requirements.txt
│   ├── core/                      # Módulos core (recon, monitor, etc.)
│   ├── data/                      # SQLite DB + dados
│   └── ui/                        # Dashboard UI
│
├── docker-compose.yml             # 🐳 Orquestração Docker (kali-network)
├── docker-up.sh                   # Script para iniciar Docker Compose
├── validate-docker.sh             # Validação do setup Docker
└── [outros arquivos de config]
```

---

## 🚀 Como Começar

### 1️⃣ Inicialização Rápida (Docker)

```bash
# Validar Docker setup
./validate-docker.sh

# Iniciar containers
docker compose up --build

# Acessar aplicação
# Frontend:  http://localhost:5190
# Backend:   http://localhost:8001
# API Docs:  http://localhost:8001/docs
```

### 2️⃣ Desenvolvimento Local

```bash
# Backend
cd backend
python main_fastapi.py

# Frontend (outro terminal)
cd frontend
npm install
npm run dev
```

---

## ✨ Destaques da V3.0

### ✅ Tecnologias
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python 3.11 + SQLite
- **DevOps:** Docker Compose + healthchecks + volumes persistentes
- **Network:** Isolada em bridge `kali-network`

### ✅ Segurança
- TypeScript strict mode
- ESLint para code quality
- Validação de tipos em runtime
- CORS configurado

### ✅ Organização
- 🧹 Zero código legado (higienização absoluta)
- 📦 CSS modular (global.css + componentes individuais)
- 📚 Documentação centralizada em `docs/`
- 🎯 Estrutura clara e manutenível

---

## 🔗 Links Rápidos

| Recurso | Link |
|---------|------|
| 📖 Para Iniciantes | [QUICKSTART_V3.md](QUICKSTART_V3.md) |
| 🐳 Para DevOps | [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) |
| 🗺️ Mapa do Projeto | [PROJECT_MAP.md](PROJECT_MAP.md) |
| 🌐 Dashboard | [README_WEB_DASHBOARD.md](README_WEB_DASHBOARD.md) |
| 🎨 CSS Guide | [CSS_INTEGRATION_GUIDE.md](CSS_INTEGRATION_GUIDE.md) |
| ✅ Final Status | [STATUS_FINAL.md](STATUS_FINAL.md) |

---

## 📞 Suporte

Todos os documentos estão organizados em `docs/`. Para navegar:

1. Comece por **QUICKSTART_V3.md** (iniciante)
2. Consulte **PROJECT_MAP.md** (arquitetura)
3. Use **STATUS_FINAL.md** (verificação de status)
4. Leia documentação específica conforme necessário

**Dúvidas?** Verifique:
- [STATUS_FINAL.md](STATUS_FINAL.md) - Troubleshooting
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Problemas Docker
- [README_WEB_DASHBOARD.md](README_WEB_DASHBOARD.md) - Problemas Frontend

---

**Última atualização:** 25 de Maio de 2026  
**Status:** ✅ Pronto para Deployment
