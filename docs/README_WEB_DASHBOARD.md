# KALI-CORE - Dashboard Web Local

**Versão:** 1.0.0  
**Status:** OPERACIONAL  
**Porta:** 8000

---

## 📋 Visão Geral

O KALI-CORE foi reestruturado para ter um Dashboard Web Local, substituindo a interface de terminal ncurses por uma interface moderna baseada em FastAPI e WebSocket.

---

## 🚀 Inicialização Rápida

### 1. Instalar Dependências

```bash
cd backend
pip3 install --break-system-packages -r requirements.txt
```

### 2. Iniciar Servidor

```bash
cd backend
python3 main_fastapi.py
```

O servidor iniciará em `http://0.0.0.0:8000`

### 3. Acessar Dashboard

Abra o navegador e acesse:
```
http://localhost:8000
```

Ou abra o arquivo `frontend/index.html` diretamente no navegador.

---

## 📁 Estrutura de Diretórios

```
projeto-kali/
├── backend/
│   ├── main_fastapi.py          # Servidor FastAPI + Orquestrador
│   ├── requirements.txt         # Dependências Python
│   ├── core/                    # Módulos do sistema
│   │   ├── recon.py
│   │   ├── monitor.py
│   │   ├── deep_packet.py
│   │   └── arsenal.py
│   ├── ui/
│   │   └── dashboard.py         # Dashboard legado (ncurses)
│   └── data/                    # Dados e logs
│       ├── reports/
│       └── network/
├── frontend/
│   └── index.html               # Dashboard Web (Tailwind CSS)
└── README_WEB_DASHBOARD.md     # Este arquivo
```

---

## 🔌 API REST Endpoints

### GET `/`
Retorna informações do sistema

### GET `/api/status`
Retorna status geral do sistema (CPU, memória, temperatura)

### GET `/api/fases`
Retorna status das 8 fases de invasão

### GET `/api/bandeiras`
Retorna bandeiras disponíveis

### GET `/api/logs`
Retorna últimos 100 logs

### WebSocket `/ws/logs`
Transmite logs em tempo real

### POST `/api/injecao/{tipo}`
Executa injeção sutil (web, database, extracao)

---

## 🎨 Frontend

### Layout

O dashboard web possui 3 colunas:

**Coluna 1: Status das 8 Fases**
- Status das 8 fases de invasão
- Sem redundância de dados

**Coluna 2: Log Stream**
- Console em tempo real via WebSocket
- Últimos 100 logs

**Coluna 3: Inventário de Bandeiras e Botão de Injeção Sutil**
- Bandeiras disponíveis
- Botões para injeção sutil (web, database, extracao)

### Tecnologias

- Tailwind CSS (via CDN)
- WebSocket para logs em tempo real
- Fetch API para chamadas REST
- JavaScript puro (sem frameworks)

---

## 🔧 Configuração

### Alvo Dinâmico
O alvo não é mais configurado em código. Use a interface web:

1. Abrir `http://localhost:8000`
2. Clicar em "MÓDULO DO ARSENAL"
3. Digitar alvo no campo [ ALVO: ]
4. Clicar [ INICIAR OPERAÇÃO ]

Cada operação é rastreada com seu alvo específico no banco de dados (`backend/models.py::AttackHistory.target_ip`).

### Porta

A porta padrão é `8000`. Para alterar, edite `backend/main_fastapi.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=SUA_PORTA_AQUI)
```

---

## 🎯 Preservação de Lógica

A lógica de ataque, os módulos de entropia TLS e o DNS Brute Force foram preservados. Apenas a interface foi alterada para expor os resultados via API.

---

## 📊 Monitoramento

O dashboard atualiza automaticamente:
- Status das fases: a cada 5 segundos
- Bandeiras: a cada 5 segundos
- Hardware: a cada 5 segundos
- Logs: em tempo real via WebSocket

---

## ⚠️ Notas

- O servidor Uvicorn deve ser executado no diretório `backend/`
- O frontend pode ser acessado via `http://localhost:8000` ou abrindo `frontend/index.html` diretamente
- As dependências Python foram instaladas com `--break-system-packages` devido ao ambiente Kali Linux
- Conflitos de versão com o theharvester não afetam o funcionamento do FastAPI

---

## 🚨 Troubleshooting

### Servidor não inicia

Verifique se as dependências estão instaladas:
```bash
pip3 install --break-system-packages fastapi uvicorn websockets psutil
```

### WebSocket não conecta

Verifique se o servidor está rodando na porta 8000:
```bash
curl http://localhost:8000/api/status
```

### Logs não aparecem

Verifique se o arquivo `data/reports/pentest.log` existe e tem permissões de escrita.

---

## ✅ Status do Sistema

- ✅ Backend FastAPI operacional
- ✅ WebSocket logs em tempo real
- ✅ Frontend Tailwind CSS
- ✅ Grid 3 colunas
- ✅ API REST endpoints
- ✅ Preservação de lógica de ataque

**Motor roncando no backend, dados brilhando no navegador!**
