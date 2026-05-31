# 🏗️ ARQUITETURA VISUAL - KALI-CORE V3.0

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║          KALI-CORE V3.0 - CAMADAS ARQUITETURAIS                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 1: APRESENTAÇÃO (Frontend)                                           │
│                                                                             │
│  React 18 + Vite + TypeScript (Port 5190)                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Dashboard                                                            │  │
│  │ ┌─────────────────────────────┐  ┌────────────────────────────────┐ │  │
│  │ │ ATAQUES (Tela Principal)    │  │ AUDITORIA & COMPLIANCE (Modal) │ │  │
│  │ │ - InjecaoSutil              │  │ - Filtros vulnerabilidades    │ │  │
│  │ │ - Seleção de alvo           │  │ - Gerar relatório             │ │  │
│  │ │ - Tácticas                  │  │ - Exportar dados              │ │  │
│  │ │ - Iniciar Operação          │  │ - Tags e classificação        │ │  │
│  │ │ - Status em tempo real      │  │                               │ │  │
│  │ └─────────────────────────────┘  └────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  HTTP ↕ REST API (JSON)                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 2: API (Backend)                                                     │
│                                                                             │
│  FastAPI 0.104.1 + Python 3.11 (Port 8001)                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Endpoints                                                            │  │
│  │ ├── GET  /api/targets              (Listar alvos)                   │  │
│  │ ├── POST /api/operations           (Iniciar operação)               │  │
│  │ ├── GET  /api/vulnerabilities      (Listar vulnerabilidades)        │  │
│  │ ├── GET  /api/audit                (Histórico de auditoria)         │  │
│  │ ├── POST /api/ativos               (CRUD novo schema)               │  │
│  │ └── GET  /docs                     (Swagger UI)                     │  │
│  │                                                                      │  │
│  │ Middleware                                                           │  │
│  │ ├── CORS                                                            │  │
│  │ ├── Logging                                                         │  │
│  │ ├── Error Handling                                                  │  │
│  │ └── Authentication (future)                                         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  SQLAlchemy ORM ↕ SQL                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 3: MODELOS & ORM (SQLAlchemy)                                        │
│                                                                             │
│  backend/models.py                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ NOVO SCHEMA (7 tabelas)                                              │  │
│  │                                                                      │  │
│  │  Ativo (UUID)                                                        │  │
│  │    ├── Identificadores (1:N) → IP, MAC, IMEI, Hostname, Serial      │  │
│  │    ├── InterfaceDeRede (1:N) → Ethernet, Wi-Fi, Bluetooth, 4G/5G    │  │
│  │    ├── Coletas (1:N)                                                │  │
│  │    │   └── DadosBrutos (1:N, JSONB) → Flexibilidade total           │  │
│  │    ├── Eventos (1:N) → Auditoria (descoberta, ip_alterado, etc)     │  │
│  │    └── Tags (N:N) → Classificação (Produção, Crítico, IoT, etc)     │  │
│  │                                                                      │  │
│  │ LEGADO (4 tabelas - compatibilidade)                                │  │
│  │    ├── Alvo → AlvoLegado (alias)                                    │  │
│  │    ├── ConfigAtaque → ConfigAtaqueLegado                            │  │
│  │    ├── HistoricoOperacoes → HistoricoOperacoesLegado               │  │
│  │    └── VulnerabilidadesOcorrencias → VulnerabilidadesOcorrenciasLe  │  │
│  │                                                                      │  │
│  │ COMPATIBILIDADE: Código antigo funciona sem mudanças! ✅            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  psycopg2 (driver PostgreSQL)                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 4: BANCO DE DADOS (PostgreSQL)                                       │
│                                                                             │
│  PostgreSQL 16 Alpine (Port 5432 - isolado em rede)                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Database: kali_core (User: kali / Password: kali)                   │  │
│  │                                                                      │  │
│  │  ╔════════════════════════════════════════════════════════════╗    │  │
│  │  ║              SCHEMA NOVO (7 tabelas)                       ║    │  │
│  │  ╠════════════════════════════════════════════════════════════╣    │  │
│  │  ║ ✓ ativos                (Inventário)                       ║    │  │
│  │  ║ ✓ identificadores       (IDs múltiplos)                    ║    │  │
│  │  ║ ✓ interfaces_de_rede    (Meios de comunicação)             ║    │  │
│  │  ║ ✓ coletas              (Histórico de coletas)              ║    │  │
│  │  ║ ✓ dados_brutos         (JSONB - Flexibilidade)            ║    │  │
│  │  ║ ✓ eventos              (Auditoria completa)                ║    │  │
│  │  ║ ✓ tags                 (Classificação)                     ║    │  │
│  │  ╠════════════════════════════════════════════════════════════╣    │  │
│  │  ║              SCHEMA LEGADO (5 tabelas)                     ║    │  │
│  │  ╠════════════════════════════════════════════════════════════╣    │  │
│  │  ║ ✓ alvos                 (compatibilidade)                  ║    │  │
│  │  ║ ✓ config_ataque         (compatibilidade)                  ║    │  │
│  │  ║ ✓ historico_operacoes   (compatibilidade)                  ║    │  │
│  │  ║ ✓ vulnerabilidades_ocorrencias (compatibilidade)           ║    │  │
│  │  ║ ✓ attack_history        (compatibilidade)                  ║    │  │
│  │  ╚════════════════════════════════════════════════════════════╝    │  │
│  │                                                                      │  │
│  │  Volume Docker: postgres_data (persistência)                        │  │
│  │  Network: kali-network (172.20.0.0/16)                              │  │
│  │  Healthcheck: pg_isready -U kali -d kali_core                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Persistência → Volume Docker `postgres_data`                              │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                       FLUXO DE DADOS COMPLETO                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1️⃣  USUÁRIO INTERAGE
    └─ Acessa http://localhost:5190
    └─ Clica "Iniciar Operação"
    └─ Insere IP/Domínio alvo
    └─ Seleciona táticas

2️⃣  FRONTEND ENVIA
    └─ HTTP POST /api/operations
    └─ JSON: {target: "192.168.1.100", tactics: [...]}

3️⃣  API PROCESSA
    └─ FastAPI recebe em routes
    └─ Valida input (Pydantic models)
    └─ Orquestra operações de ataque

4️⃣  ORM MAPEIA
    └─ SQLAlchemy converte para SQL
    └─ Cria/atualiza Alvos, Operações, Vulnerabilidades

5️⃣  BANCO ARMAZENA
    └─ PostgreSQL insere/atualiza registros
    └─ JSONB armazena dados flexíveis
    └─ Eventos registram auditoria

6️⃣  RESULTADO RETORNA
    └─ SQL → Python objects
    └─ Python objects → JSON
    └─ JSON → Frontend
    └─ Frontend atualiza Dashboard em tempo real

7️⃣  AUDITORIA VISUALIZA
    └─ Usuário clica "[ AUDITORIA ]"
    └─ Modal abre histórico
    └─ Usuário seleciona vulnerabilidades
    └─ Gera "[ COMPLIANCE ]" (PDF/Excel)

╔═══════════════════════════════════════════════════════════════════════════════╗
║                      CONTAINERS DOCKER INTERCONECTADOS                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Frontend       │◄────►│    Backend       │◄────►│   PostgreSQL     │
│  kali-core       │ HTTP │   kali-core      │ SQL  │  kali-core       │
│  Port 5190       │ REST │   Port 8001      │      │  Port 5432       │
│                  │      │                  │      │                  │
│ React 18 + Vite  │      │ FastAPI+Python   │      │ PostgreSQL 16    │
│                  │      │                  │      │                  │
│ Hot-reload via   │      │ Healthcheck: ✓   │      │ Healthcheck: ✓   │
│ volumes          │      │                  │      │                  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
         │                         │                         │
         │                         │                         │
         └────────────────────────────────────────────────────┘
              kali-network (bridge isolado 172.20.0.0/16)
                     Container restart: unless-stopped

╔═══════════════════════════════════════════════════════════════════════════════╗
║                         VOLUMES E PERSISTÊNCIA                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Host Machine                          Docker Container
────────────────────────────────────────────────────────

/home/eu/Documentos/GitHub/           /app              (Backend)
projeto-kali/
├── frontend/src/         ──bind───► /app/src          (Hot-reload)
├── frontend/public/      ──bind───► /app/public
├── backend/              ──bind───► /app              (Código)
├── backend/data/         ──bind───► /app/data         (Temporários)
│
└── (Docker daemon)
    └── postgres_data volume ──────────► /var/lib/postgresql/data
                                         (PostgreSQL - PERSISTÊNCIA)

╔═══════════════════════════════════════════════════════════════════════════════╗
║                    EXEMPLO: NOVA ENTRADA NO BANCO                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Frontend Action:                 Backend Processing:              Database Result:
────────────────────────────────────────────────────────────────────────────────

User clicks                      1. FastAPI recebe             INSERT INTO ativos
"Iniciar Operação"                  {target: "192.168.1.50"}    (id, tipo, nome, status)
    │                                                           VALUES (uuid, 'PC',
Input: IP 192.168.1.50          2. SQLAlchemy cria               'workstation', 'ativo');
Select tactics:                     Ativo object
- ReconFast                                                     INSERT INTO 
- SqlInjection               3. Valida relacionamentos           identificadores
                                (tipo de ativo, tags)           (ativo_id, tipo, valor)
                                                                VALUES (uuid, 'IP',
Click "[ INICIAR ]"          4. Executa tático                  '192.168.1.50');
    │                           (recon, sqlmap, etc)
    │                                                           INSERT INTO eventos
    ├─► HTTP POST             5. Captura resultado              (ativo_id, tipo, dados)
        /api/operations       (sucesso/erro, payload,           VALUES (uuid, 'descoberta',
        Content-Type:            response_code)                 {...});
        application/json
                               6. Cria HistoricoOperacoes       UPDATE ativos
                               e Vulnerabilidades               SET atualizado_em = NOW();
                               
                               7. Converte Python → JSON

Result shown                  8. Retorna JSON
in Dashboard                  
                               ┌─────────────────────┐
                               │ 200 OK              │
                               │ {                   │
                               │  "sucesso": true,   │
                               │  "operacao_id": 1,  │
                               │  "vulnerabilidades" │
                               │  : [...]            │
                               │ }                   │
                               └─────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║                              SECURITY MODEL                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

✓ UUIDs (não IDs sequenciais) - Dificulta enumeração
✓ PostgreSQL isolado - Porta 5432 não exposta (apenas rede bridge)
✓ Environment variables - Credenciais não em código
✓ CORS habilitado - Apenas origem localhost:5190
✓ Auditoria completa - Todos os eventos registrados
✓ Snapshots de dados - Rastreamento de mudanças
✓ Network isolada - bridge 172.20.0.0/16

╔═══════════════════════════════════════════════════════════════════════════════╗
║                          PERFORMANCE FEATURES                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

✓ JSONB indexable - Queries eficientes em dados legados
✓ Connection pooling - SQLAlchemy gerencia
✓ Lazy loading - Relacionamentos sob demanda
✓ Prepared statements - Proteção contra SQL injection
✓ Volume Docker - I/O mais rápido que bind mount
✓ Hot-reload - Vite detecta mudanças automaticamente

```

---

## 📈 EVOLUÇÃO DO PROJETO

```
V1.0 (Origem)          V2.0 (Melhoria)       V3.0 (Atual)         V4.0 (Próxima)
─────────────────────────────────────────────────────────────────────────────────

SQLite                  SQLite                PostgreSQL           PostgreSQL
Single file             Estruturado           Distribuído          Replicado
AttackHistory           Novo schema +         7 tabelas +          Particionado
                        Legado                5 legado             Sharded

Sem auditoria          Auditoria básica      Eventos com          Full audit trail
                                             snapshots             com compliance

No Docker              Docker V1              Docker V3             Docker swarm
                       (2 containers)         (3 containers)       (clustering)

SQLite drivers         SQLite + Alembic      PostgreSQL +          Aurora/Cloud
                                             Alembic              SQL

Código hardcoded       Environment vars      Vars + .env file     Secrets manager
                                             (12-factor)          (Vault/AWS)
```

---

**KALI-CORE V3.0 - Pronto para a próxima evolução! 🚀**
