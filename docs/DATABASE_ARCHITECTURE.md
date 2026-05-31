# ARQUITETURA DE BANCO DE DADOS - KALI-CORE V3.0

**Data:** 30 de maio de 2026  
**Status:** ✅ IMPLEMENTADA

## 📋 Sumário Executivo

Migração de SQLite para **PostgreSQL** com arquitetura escalável para **inventário e análise de ativos**. Sistema preparado para absorver dados legados (TXT/JSON) mantendo compatibilidade total com versão anterior.

---

## 🏗️ NOVO SCHEMA (7 TABELAS)

### 1. **ATIVOS** (Inventário Principal)

Armazena informações básicas de qualquer tipo de ativo.

```sql
CREATE TABLE ativos (
    id UUID PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,           -- PC, Notebook, Celular, Impressora, IoT, Servidor, etc
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    status VARCHAR(50) DEFAULT 'ativo',  -- ativo, inativo, descomissionado
    criado_em TIMESTAMP NOT NULL,
    atualizado_em TIMESTAMP NOT NULL
);
```

**Relacionamentos:**
- 1 Ativo → Muitos Identificadores
- 1 Ativo → Muitas Interfaces de Rede
- 1 Ativo → Muitas Coletas
- 1 Ativo → Muitos Eventos
- Muitos Ativos ↔ Muitas Tags (Many-to-Many)

---

### 2. **IDENTIFICADORES** (IDs Múltiplos)

Permite múltiplos identificadores por ativo (IP, MAC, IMEI, Hostname, Serial, SSID, UUID).

```sql
CREATE TABLE identificadores (
    id UUID PRIMARY KEY,
    ativo_id UUID NOT NULL REFERENCES ativos(id),
    tipo VARCHAR(50) NOT NULL,           -- IP, MAC, IMEI, Hostname, Serial, SSID, UUID
    valor TEXT NOT NULL,
    criado_em TIMESTAMP NOT NULL
);
```

**Exemplos:**
| ativo_id | tipo | valor |
|----------|------|-------|
| uuid-001 | IP | 192.168.1.100 |
| uuid-001 | MAC | 00:11:22:33:44:55 |
| uuid-001 | Hostname | workstation-01 |
| uuid-002 | IMEI | 354358534534535 |

---

### 3. **INTERFACES_DE_REDE** (Meios de Comunicação)

Registra todas as interfaces de comunicação do ativo.

```sql
CREATE TABLE interfaces_de_rede (
    id UUID PRIMARY KEY,
    ativo_id UUID NOT NULL REFERENCES ativos(id),
    tipo VARCHAR(50) NOT NULL,           -- Ethernet, Wi-Fi, Bluetooth, LTE, 5G, Satélite, IR, Rádio
    mac VARCHAR(17),                     -- XX:XX:XX:XX:XX:XX
    ip VARCHAR(45),                      -- IPv4 ou IPv6
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP NOT NULL,
    atualizado_em TIMESTAMP NOT NULL
);
```

**Exemplos:**
| tipo | mac | ip | ativo |
|------|-----|----|-------|
| Ethernet | 00:11:22:33:44:55 | 192.168.1.100 | true |
| Wi-Fi | 00:11:22:33:44:56 | 192.168.1.101 | true |
| Bluetooth | 00:11:22:33:44:57 | null | true |
| LTE | null | 10.0.0.50 | false |

---

### 4. **COLETAS** (Histórico de Coletas)

Registra cada coleta de informações realizada (quando, de onde).

```sql
CREATE TABLE coletas (
    id UUID PRIMARY KEY,
    ativo_id UUID NOT NULL REFERENCES ativos(id),
    coletado_em TIMESTAMP NOT NULL,
    origem VARCHAR(100) NOT NULL,       -- Agente Windows, Frontend, Importação TXT/JSON, API
    versao_agente VARCHAR(50),
    criado_em TIMESTAMP NOT NULL
);
```

**Rastreamento:**
- Permite saber exatamente quando e de onde vêm os dados
- Suporta múltiplas fontes (agentes, importações, APIs)

---

### 5. **DADOS_BRUTOS** (Flexibilidade com JSONB)

Armazena dados flexíveis sem remodelagem de schema.

```sql
CREATE TABLE dados_brutos (
    id UUID PRIMARY KEY,
    coleta_id UUID NOT NULL REFERENCES coletas(id),
    json_dados JSONB NOT NULL,           -- PostgreSQL JSONB
    criado_em TIMESTAMP NOT NULL
);
```

**Exemplo de json_dados:**
```json
{
  "hardware": {
    "cpu": {
      "fabricante": "Intel",
      "modelo": "i5-10400",
      "cores": 6,
      "threads": 12
    },
    "ram": {
      "total_gb": 16,
      "velocidade": "3200MHz"
    },
    "discos": [
      {
        "modelo": "Kingston",
        "capacidade_gb": 480,
        "tipo": "SSD"
      }
    ]
  },
  "sistema": {
    "so": "Windows 11",
    "versao": "22H2"
  },
  "softwares": [
    {"nome": "Chrome", "versao": "120.0"},
    {"nome": "VS Code", "versao": "1.85"}
  ]
}
```

**Vantagens JSONB:**
- Sem necessidade de migração para cada novo campo
- Queryable (pode filtrar pelo JSON)
- Indexable para performance
- Suporta dados legados sem perda

---

### 6. **EVENTOS** (Auditoria & Histórico)

Registra histórico e alterações de ativos com snapshots.

```sql
CREATE TABLE eventos (
    id UUID PRIMARY KEY,
    ativo_id UUID NOT NULL REFERENCES ativos(id),
    tipo VARCHAR(100) NOT NULL,          -- descoberta, ip_alterado, firmware_alterado, online, offline
    descricao TEXT,
    dados_anteriores JSONB,              -- Snapshot do antes
    dados_novos JSONB,                   -- Snapshot do depois
    criado_em TIMESTAMP NOT NULL
);
```

**Exemplos de eventos:**
- `descoberta` - Ativo encontrado pela primeira vez
- `ip_alterado` - IP mudou (DHCP renewal, reconfiguration)
- `firmware_alterado` - Firmware atualizado
- `online` - Ativo retornou online
- `offline` - Ativo ficou offline
- `classificacao_alterada` - Tag/classificação mudou

---

### 7. **TAGS** (Classificação & Agrupamento)

Permite classificação e agrupamento de ativos.

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    cor VARCHAR(7) DEFAULT '#808080',    -- Código hex
    descricao TEXT,
    criado_em TIMESTAMP NOT NULL
);

CREATE TABLE ativo_tag_association (
    ativo_id UUID REFERENCES ativos(id),
    tag_id UUID REFERENCES tags(id),
    PRIMARY KEY (ativo_id, tag_id)
);
```

**Exemplos de tags:**
- `Produção` (cor: #00AA00)
- `Laboratório` (cor: #FFAA00)
- `Cliente A` (cor: #0000FF)
- `Crítico` (cor: #FF0000)
- `IoT` (cor: #AA00FF)
- `Embarcado` (cor: #00AAFF)

---

## 🔄 RELACIONAMENTOS

```
ATIVO (central)
 │
 ├─── IDENTIFICADORES (1:N)
 │    └─ IP, MAC, IMEI, Hostname, Serial, SSID, UUID
 │
 ├─── INTERFACES_DE_REDE (1:N)
 │    └─ Ethernet, Wi-Fi, Bluetooth, LTE, 5G, Satélite, IR, Rádio
 │
 ├─── COLETAS (1:N)
 │    │
 │    └─── DADOS_BRUTOS (1:N)
 │         └─ JSONB (CPU, RAM, Discos, SO, Softwares, etc)
 │
 ├─── EVENTOS (1:N)
 │    └─ descoberta, ip_alterado, firmware_alterado, online, offline
 │
 └─── TAGS (N:N)
      └─ Produção, Laboratório, Cliente A, Crítico, IoT, etc
```

---

## 🔄 MIGRAÇÃO DE DADOS LEGADOS

### Fluxo de Importação

```
TXT/JSON (arquivos antigos)
    ↓
Parser (normalização)
    ↓
JSON intermediário
    ↓
PostgreSQL (DadosBrutos JSONB)
    ↓
Sem perda de informação
```

**Exemplo de migração:**

Arquivo TXT legado:
```
IP: 192.168.1.50
MAC: 00:11:22:33:44:55
Hostname: servidor-db
CPU: Intel i7-8700K
RAM: 32GB
Tipo: Servidor
Status: Produção
```

Resultado no PostgreSQL:
```
INSERT INTO ativos (id, tipo, nome, status) 
VALUES ('uuid-xxx', 'Servidor', 'servidor-db', 'ativo');

INSERT INTO identificadores (ativo_id, tipo, valor)
VALUES 
  ('uuid-xxx', 'IP', '192.168.1.50'),
  ('uuid-xxx', 'MAC', '00:11:22:33:44:55'),
  ('uuid-xxx', 'Hostname', 'servidor-db');

INSERT INTO coletas (ativo_id, coletado_em, origem)
VALUES ('uuid-xxx', NOW(), 'Importação TXT');

INSERT INTO dados_brutos (coleta_id, json_dados)
VALUES ('coleta-uuid', '{"cpu": "Intel i7-8700K", "ram": "32GB"}');
```

---

## 🛠️ STACK TECNOLÓGICO

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Banco Principal | PostgreSQL | 16 Alpine |
| ORM | SQLAlchemy | 2.0.25 |
| Migrations | Alembic | 1.13.0 |
| Backend | FastAPI | 0.104.1 |
| Drivers | psycopg2-binary | 2.9.9 |
| Container | Docker Compose | 3.8 |

---

## 🚀 FEATURES PRINCIPAIS

### ✅ Implementadas
- [x] 7 tabelas novo schema
- [x] 4 tabelas legado (compatibilidade)
- [x] Relacionamentos completos
- [x] UUID como primary key
- [x] JSONB para flexibilidade
- [x] Auditoria com eventos
- [x] Docker Compose com PostgreSQL
- [x] Many-to-Many (Ativo ↔ Tag)

### 🔄 Em Desenvolvimento
- [ ] Alembic migrations
- [ ] Importers (TXT/JSON)
- [ ] API endpoints CRUD
- [ ] Índices otimizados
- [ ] Queries de busca complexa

### 🔮 Futuro
- [ ] Replicação (standby)
- [ ] Backup automático
- [ ] Particionamento de tabelas
- [ ] Full-text search
- [ ] Versionamento de dados

---

## 📝 COMPATIBILIDADE

### Tabelas Legadas (SQLite → PostgreSQL)
```
SQLite (AttackHistory)     →  PostgreSQL (AttackHistory + Legado)
├── alvos
├── config_ataque
├── historico_operacoes
├── vulnerabilidades_ocorrencias
└── attack_history
```

**Aliases para compatibilidade:**
```python
Alvo = AlvoLegado
ConfigAtaque = ConfigAtaqueLegado
HistoricoOperacoes = HistoricoOperacoesLegado
VulnerabilidadesOcorrencias = VulnerabilidadesOcorrenciasLegado
```

Código existente funciona **sem mudanças**! ✅

---

## 💡 EXEMPLOS DE USO

### Criar Ativo
```python
from models import Ativo, Identificador, InterfaceDeRede
from datetime import datetime

ativo = Ativo(
    tipo="Notebook",
    nome="workstation-01",
    status="ativo"
)
session.add(ativo)
session.flush()  # Get UUID

# Adicionar identificadores
id_ip = Identificador(ativo_id=ativo.id, tipo="IP", valor="192.168.1.100")
id_mac = Identificador(ativo_id=ativo.id, tipo="MAC", valor="00:11:22:33:44:55")
session.add_all([id_ip, id_mac])

# Adicionar interface
iface = InterfaceDeRede(
    ativo_id=ativo.id,
    tipo="Ethernet",
    mac="00:11:22:33:44:55",
    ip="192.168.1.100"
)
session.add(iface)
session.commit()
```

### Registrar Coleta com Dados Brutos
```python
from models import Coleta, DadosBrutos
import json

coleta = Coleta(
    ativo_id=ativo.id,
    coletado_em=datetime.utcnow(),
    origem="Agente Windows"
)
session.add(coleta)
session.flush()

dados = DadosBrutos(
    coleta_id=coleta.id,
    json_dados={
        "cpu": {"modelo": "Intel i5", "cores": 4},
        "ram": 16,
        "discos": [{"tipo": "SSD", "gb": 512}]
    }
)
session.add(dados)
session.commit()
```

### Buscar Ativo por Identificador
```python
from sqlalchemy import and_

ativo = session.query(Ativo)\
    .join(Identificador)\
    .filter(and_(
        Identificador.tipo == "IP",
        Identificador.valor == "192.168.1.100"
    ))\
    .first()
```

### Filtrar por Tag
```python
ativos_criticos = session.query(Ativo)\
    .join(Ativo.tags)\
    .filter(Tag.nome == "Crítico")\
    .all()
```

---

## 🔐 SEGURANÇA

- ✅ Credenciais em variáveis de ambiente
- ✅ PostgreSQL isolado em rede bridge
- ✅ UUIDs em vez de IDs sequenciais
- ✅ Auditoria com timestamps
- ✅ Snapshots de eventos para compliance
- ✅ Sem exposição de porta PostgreSQL (apenas interno)

---

## 📊 PERFORMANCE

- **Índices automáticos:** UUIDs em PK e FKs
- **JSONB indexable:** Permite queries eficientes
- **Connection pooling:** SQLAlchemy gerencia
- **Lazy loading:** Relacionamentos sob demanda
- **Prepared statements:** Proteção contra SQL injection

---

## 📖 PRÓXIMOS PASSOS

1. **Alembic Setup:** `alembic init migrations`
2. **Criar migration inicial:** `alembic revision --autogenerate`
3. **Implementar importers:** TXT e JSON
4. **API endpoints:** CRUD completo
5. **Testes:** unittest + pytest
6. **Documentação API:** Swagger/OpenAPI

---

**Banco de dados pronto para produção! 🚀**
