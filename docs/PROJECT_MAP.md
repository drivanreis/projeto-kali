# PROJECT_MAP - KALI-CORE
**Última atualização:** 2026-05-24 (v2.2 - Reestruturação de Auditoria)

## Visão Geral
O KALI-CORE é um sistema unificado de intrusão e monitoramento de rede, projetado para operações de reconhecimento e penetração em tempo real. O sistema é composto por módulos independentes que operam em threads separadas, orquestrados pelo `main_fastapi.py`.

**Nova Prioridade de Inteligência:** A operação é contra **alvo dinâmico fornecido pelo usuário** via interface web. Cada operação é rastreada com seu alvo específico no banco de dados.

## 🎯 Definição de Alvo (Ativo)

Um **alvo** (ou **ativo**) é qualquer dispositivo, sistema, interface ou infraestrutura capaz de transmitir, receber ou intermediar dados através de algum meio de comunicação.

### Características dos Ativos:
- **Meios de Comunicação Inclusos:**
  - Wi-Fi (wireless local)
  - Ethernet (cabeado)
  - Bluetooth (comunicação de curto alcance)
  - Rede Móvel (SIM/celular 4G/5G)
  - Satélite (comunicação orbital)
  - Infravermelho (IR)
  - Rádio (frequências diversas)
  - Fibra Óptica (alta velocidade)
  - Cabo Submarino (comunicação intercontinental)

- **Identificadores Únicos:**
  - Endereço MAC (Media Access Control)
  - Endereço IP (IPv4/IPv6)
  - IMEI (Identificador de Equipamentos Móveis)
  - Outros identificadores únicos de hardware/software
  - **Obs:** Mesmo sem hostname/SSID visível, um ativo continua sendo rastreável

- **Exemplos de Ativos:**
  - Computadores (desktop, notebook, servidor)
  - Smartphones e tablets
  - Roteadores e switches
  - Impressoras de rede
  - Câmeras IP
  - Tomadas inteligentes
  - Módulos Sonoff (automação)
  - Sensores IoT
  - Equipamentos embarcados
  - Qualquer dispositivo "silencioso" ou sem identificação amigável

### Implicação para o KALI-CORE:
Todos esses ativos são potenciais alvos de operações de reconhecimento, análise de vulnerabilidades e testes de penetração realizado pelo sistema.

**Definição de Vitória:** O objetivo final não é a destruição, mas a marcação de território (Proof of Concept). A vitória é definida por cinco ações de baixo impacto e alto valor:
1. Injeção Visual (Web Defacement Sutil)
2. Injeção de Persistência em Dados (Database Entry)
3. Extração Simbólica (Filtro Ético)
4. Scanner de Protocolo Evasivo
5. Envenenamento de Cache ARP

## Banco de Dados - Novo Schema (v2.2)
Modelo relacional com 4 tabelas + 1 legada para compatibilidade:

### Tabela 1: `Alvos`
```sql
CREATE TABLE alvos (
    id INTEGER PRIMARY KEY,
    ip_dominio VARCHAR(255) UNIQUE NOT NULL,
    data_criacao DATETIME DEFAULT now()
)
```

### Tabela 2: `ConfigAtaque`
```sql
CREATE TABLE config_ataque (
    id INTEGER PRIMARY KEY,
    alvo_id INTEGER FOREIGN KEY,
    porta INTEGER,
    protocolo VARCHAR(50),
    servico_detectado VARCHAR(100),
    timestamp DATETIME DEFAULT now()
)
```

### Tabela 3: `HistoricoOperacoes`
```sql
CREATE TABLE historico_operacoes (
    id INTEGER PRIMARY KEY,
    alvo_id INTEGER FOREIGN KEY,
    config_id INTEGER FOREIGN KEY,
    attack_phase VARCHAR(50),
    attack_type VARCHAR(100),
    payload TEXT,
    success BOOLEAN DEFAULT FALSE,
    response_code INTEGER,
    response_data TEXT (JSON),
    status_fase VARCHAR(50),
    timestamp DATETIME,
    duration_ms FLOAT,
    error_message TEXT,
    lesson_learned TEXT,
    confidence_score FLOAT
)
```

### Tabela 4: `AnaliseEstrategica` (Motor de Análise)
```sql
CREATE TABLE analise_estrategica (
    id INTEGER PRIMARY KEY,
    operacao_id INTEGER FOREIGN KEY,
    tempo_estimado_invasao INTEGER,
    criticidade VARCHAR(20),
    flags_detectadas TEXT (JSON),
    recomendacao_invisibilidade TEXT,
    timestamp DATETIME
)
```

### Tabela 5: `VulnerabilidadesOcorrencias` (Vulnerabilidades Encontradas)
```sql
CREATE TABLE vulnerabilidades_ocorrencias (
    id INTEGER PRIMARY KEY,
    operacao_id INTEGER FOREIGN KEY (HistoricoOperacoes.id),
    criticidade VARCHAR(20),              -- critica, alta, media, baixa
    titulo VARCHAR(255) NOT NULL,         -- Título da vulnerabilidade
    descricao TEXT,                       -- Descrição técnica detalhada
    correcao TEXT,                        -- Passos para correção/mitigação
    timestamp DATETIME DEFAULT now()      -- Quando foi detectada
)
```
**Propósito:** Armazena cada ocorrência de vulnerabilidade encontrada durante as operações de ataque. Permite auditoria e rastreamento de quais vulnerabilidades foram detectadas em qual operação/alvo.

**Relacionamentos:** 
- `operacao_id` → Referencia `HistoricoOperacoes.id`
- Permite JOINs com `Alvos` via `HistoricoOperacoes`

**Exemplo de Uso:**
- Após scan NIKTO encontrar SQL Injection → insere 1 registro
- Após GOBUSTER encontrar /admin exposto → insere 1 registro
- Filtros modais consultam esta tabela com JOINs

### Tabela Legada: `AttackHistory` (compatibilidade)
- Mantida para dados históricos
- Novas operações usam tabelas 1-4

## Alvo Dinâmico
O alvo é agora **definido pelo usuário via interface web** ao iniciar uma operação. Não há mais alvo padrão hardcoded no código.

### Como Usar
1. Abrir dashboard em `http://localhost:8000`
2. Clicar em "MÓDULO DO ARSENAL"
3. Digitar alvo em [ INPUT ]
4. **NOVO:** Selecionar táticas de injeção (checkboxes)
5. Clicar [ INICIAR OPERAÇÃO ]

### Rastreamento de Alvo
Cada operação persiste em `historico_operacoes` com referência ao `alvo_id`, permitindo histórico isolado e análise estratégica consolidada.

## Estrutura de Diretórios

```
projeto-kali/
├── main.py              # Orquestrador principal
├── core/                # Módulos do sistema
│   ├── recon.py         # Reconhecimento e scan
│   ├── monitor.py       # Monitoramento contínuo
│   ├── deep_packet.py   # Análise profunda de pacotes (MPLS/GRE)
│   └── arsenal.py       # Orquestrador de ferramentas Kali
├── ui/                  # Interface do usuário
│   └── dashboard.py     # Dashboard unificado (ncurses)
├── frontend/            # Dashboard Web Local
│   ├── index.html       # Interface HTML/Tailwind
│   └── js/
│       └── app.js       # Lógica JavaScript
├── backend/             # Servidor FastAPI
│   ├── main_fastapi.py  # Servidor + Orquestrador
│   ├── models.py        # Modelo de Banco de Dados (Histórico de Ataques)
│   ├── requirements.txt # Dependências Python
│   ├── core/            # Módulos do sistema
│   ├── ui/              # Dashboard legado
│   └── data/            # Dados e logs
│       ├── attack_history.db # SQLite (Histórico de Ataques)
│       └── training_dataset.jsonl # Dataset para Fine-Tuning
├── data/                # Dados operacionais
│   ├── network/         # Capturas de rede (ignorado)
│   └── reports/         # Logs e relatórios (ignorado)
├── atas-dev/            # Documentação de governança
├── archive/             # Backup (ignorado)
└── PROJECT_MAP.md       # Este arquivo
```

## Fluxo de Execução

### 1. Inicialização (main.py)
- Carrega estados salvos dos módulos
- Inicia threads: RECON, MONITOR, DEEP PACKET, ARSENAL, DASHBOARD
- Verifica gatilhos automáticos (Deep Packet, Auto-Invasão)
- Salva estados periodicamente

### 2. Módulo RECON (core/recon.py)
- Scan de portas
- Banner grabbing sutil (HEAD requests)
- Verificação de serviços (web, RDP, SSH, FTP)
- Monitoramento sutil contínuo

### 3. Módulo MONITOR (core/monitor.py)
- Ping contínuo (sentinela)
- Monitoramento de portas críticas
- Alertas sonoros/visuais
- Monitoramento de conexões locais
- Monitoramento de processos de rede
- Monitoramento de recursos do sistema
- Scan passivo contínuo

### 4. Módulo DEEP PACKET (core/deep_packet.py)
- Análise de TTL (TTL Fingerprinting)
- TCP ACK Scan
- Análise de IP ID
- Monitoramento de túneis (TShark)
- Detecção de Double NAT e túneis
- **NOVO:** Detecção de MPLS labels e encapsulamento GRE
- **NOVO:** VLAN Hopping se MPLS detectado

### 5. Módulo ARSENAL (core/arsenal.py)
- Gerenciamento de subprocessos Kali
- NMAP com técnicas de evasão (fragmentação, decoy)
- NIKTO para vulnerabilidades web
- SEARCHSPLOIT para exploits
- HYDRA para força bruta
- GOBUSTER para enumeração de diretórios
- **NOVO:** WHOIS/ASN lookup para inteligência de roteamento
- **NOVO:** DNSRECON para enumeração DNS
- **NOVO:** DIG AXFR (Zone Transfer) - A BANDEIRA ESTÁ AQUI
- **NOVO:** HPING3 para testes UDP customizados (BIND)
- **NOVO:** IPv6 Enumeration para bypass de CGNAT
- **NOVO:** Web Defacement Sutil (Injeção Visual)
- **NOVO:** Database Entry (Persistência em Dados)
- **NOVO:** Extração Simbólica (Filtro Ético)
- **NOVO:** Sistema de reportagem 'BANDEIRA DISPONÍVEL'
- Auto-invasão baseada em portas abertas

### 6. DASHBOARD (ui/dashboard.py)
- Exibe status dos módulos
- Logs recentes
- Menu de comandos
- Sugestões automáticas
- **NOVO:** Painel de Bandeiras Disponíveis
- **NOVO:** Comando [b] para ver bandeiras

### 7. DASHBOARD WEB LOCAL (frontend/index.html + frontend/js/app.js)
- Interface moderna baseada em FastAPI e WebSocket
- Substitui interface ncurses por dashboard web
- **Layout 3 colunas:**
  - Coluna 1: Status das 8 Fases e Temperatura do Hardware
  - Coluna 2: Log Stream (WebSocket em tempo real)
  - Coluna 3: Inventário de Bandeiras e Botão de Injeção Sutil
- **NOVO (2026-05-17): Modal de Auditoria de Segurança**
  - Botão "🔍 AUDITORIA" no header principal
  - Design estilo terminal (fundo escuro, texto monoespaçado)
  - Marcadores coloridos por criticidade:
    - Vermelho para CRÍTICO
    - Laranja para ALTO
    - Amarelo para MÉDIO
    - Verde para BAIXO
  - Relatório integrado com 8 vulnerabilidades técnicas:
    - 2 CRÍTICAS: SECRET_KEY padrão, Credenciais expostas
    - 2 ALTAS: CORS aberto, Debug mode ativo
    - 2 MÉDIAS: Ausência de rate limiting, Logs sensíveis
    - 2 BAIXAS: Dependências desatualizadas, Headers ausentes
  - Fechar modal via botão ✕ ou clique fora

## Definição de Vitória

O objetivo final não é a destruição, mas a marcação de território (Proof of Concept). A vitória é definida por três ações de baixo impacto e alto valor:

### 1. Injeção Visual (Web Defacement Sutil)
Se o acesso à escrita de arquivos web (HTML/PHP/JS) for obtido, a meta é inserir no final do arquivo (após o rodapé) o parágrafo: `<p>🏴‍☠️ Estivemos Aqui</p>`. Isso deve ser feito sem quebrar o layout da página.

### 2. Injeção de Persistência em Dados (Database Entry)
Se o acesso ao Banco de Dados (SQL/NoSQL) for obtido, a meta é criar um novo registro (usuário, produto ou serviço) com o nome ou descrição: 'Estivemos Aqui'. Esse registro serve como evidência de escrita no banco de dados.

### 3. Extração Simbólica (Filtro Ético)
Evite extrair dados sensíveis de usuários (RG, CPFs, Senhas). A meta de extração deve ser arquivos de configuração (.env, config.php, settings.json) ou nomes de tabelas, apenas para provar que a 'chave do cofre' foi tocada.

### Diretriz de Execução
Sempre que o módulo arsenal.py ou auto_invasao encontrar uma brecha de escrita, ele deve reportar no Dashboard: 'BANDEIRA DISPONÍVEL: [Tipo de Injeção]'. Não execute a injeção automaticamente sem que eu confirme a ordem de 'Marcar a Bandeira'.

## Gatilhos Automáticos

### Deep Packet
- Porta 80 ou 443 aberta
- Servidor detectado com 404
- Inicia automaticamente análise profunda

### Auto-Invasão (NOVO - 4 Fases)
**Fase 1: Inteligência de Roteamento**
- WHOIS/ASN lookup
- Detecção de CGNAT
- IPv6 Enumeration se CGNAT detectado

**Fase 2: Ataque BIND/DNS**
- DNSRECON para enumeração DNS
- DIG AXFR (Zone Transfer) - A BANDEIRA ESTÁ AQUI

**Fase 3: Auto-invasão web**
- NIKTO para vulnerabilidades
- GOBUSTER para diretórios
- SEARCHSPLOIT para exploits

**Fase 4: Teste UDP customizado**
- HPING3 para testar resposta BIND
- Se nmap filtrado, usa hping3

## Estados Salvos
- `data/reports/recon_state.json`
- `data/reports/monitor_state.json`
- `data/reports/deep_packet_state.json`
- `data/reports/arsenal_state.json`

## Configuração
- **Hardware:** Athlon 3000G sob resfriamento forçado
- **Estado térmico:** Estável (~32°C)
- **Sistema:** Kali Linux
- **IA Local (Plano B):** Professor Kali via Ollama (http://localhost:11434)
  - Configuração: ~/.continue/config.json
  - Modelo: professor-kali
  - Provider: ollama
  - Autonomia: Operações de IA offline sem dependência externa

## Sistema de Inteligência de Logs (Histórico de Ataques)

### Banco de Dados (SQLite)
**Arquivo:** `backend/models.py`
- **Tabela:** `attack_history`
- **Campos:** IP alvo, porta, fase, tipo de ataque, payload, sucesso/falha, resposta, lição aprendida
- **Gerenciador:** `DatabaseManager`

### Endpoints FastAPI
- `POST /api/attack-history`: Salva registro de ataque
- `GET /api/attack-history`: Recupera histórico (filtros: limit, phase)
- `GET /api/attack-history/statistics`: Estatísticas agregadas
- `GET /api/attack-history/export`: Exporta dataset para fine-tuning (JSONL)

### Dataset para Fine-Tuning
**Formato:** JSONL (JSON Lines)
- **Estrutura:** instruction/input/output
- **Propósito:** Treinamento do modelo Professor Kali
- **Geração:** Automática via `export_training_dataset()`
- **Local:** `data/training_dataset.jsonl`

### Integração
- **Módulo Arsenal:** Deve salvar cada ataque no banco de dados
- **Dashboard Web:** Visualização de histórico e estatísticas
- **IA Local:** Fine-tuning com histórico acumulado
