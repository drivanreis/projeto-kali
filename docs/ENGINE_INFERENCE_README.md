# Motor de Inferência e Reação - KALI-CORE v3.0

## Visão Geral

O **Motor de Inferência** (Engine) é um sistema de resposta automática e agressiva que simula o comportamento de um **Time Azul (Blue Team)** defensivo. Ele funciona de forma **determinística** e baseada em **regras**, gerando contra-ataques automáticos em resposta a cada teste de auditoria realizado.

---

## Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Vite)                    │
│         Envia teste de segurança (INJEÇÃO SUTIL)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8001)                │
│  POST /api/attack-history (Salva Ataque + Dispara Motor)   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ENGINE DE INFERÊNCIA (engine.py)               │
│  1. Calcula Nível de Alerta (consulta histórico)           │
│  2. Seleciona Contra-Ataque (mapeamento de tipos)          │
│  3. Gera Resposta Agressiva (ações defensivas)             │
│  4. Salva como Ataque (contra-reação no banco)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLite Database                            │
│  - Histórico Original (Testes ofensivos)                   │
│  - Histórico de Reações (Contra-ataques Blue Team)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Fluxo de Funcionamento

### 1. **Recepção de Ataque**
- Frontend realiza teste de segurança (INJEÇÃO SUTIL)
- Dados são enviados: `POST /api/attack-history`
- Backend salva o ataque original no banco

### 2. **Cálculo de Nível de Alerta**
```python
nivel_alerta = engine.calcular_nivel_alerta(target_ip)
```

**Regras de Nível de Alerta:**
- **VERDE (0)**: Sem ataques recentes - operação normal
- **AMARELO (1)**: 1-2 tentativas falhadas nas últimas 24h
- **LARANJA (2)**: 3+ tentativas falhadas nas últimas 24h
- **VERMELHO (3)**: 1-2 ataques bem-sucedidos
- **CRÍTICO (4)**: 3+ ataques bem-sucedidos = Invasão confirmada

### 3. **Seleção de Contra-Ataque**
Cada tipo de teste recebe uma resposta específica:

| Tipo de Teste | Contra-Ataque | Ações Defensivas |
|---|---|---|
| **recon** | RECON_HARDENING | DNSSEC, Rotação de Portas, Encriptação Forçada, Ocultar Banners |
| **scan** | SCAN_DEFENSE | Bloquear IP, Rate Limiting, Rotacionar Portas, Honeypot |
| **exploit** | EXPLOIT_RESPONSE | Isolamento de Sistema, Memory Dump, Auditoria Completa |
| **maint** | PERSISTENCE_DETECTION | Scan Backdoors, Verificar Integridade, Monitorar Movimento Lateral |
| **exfil** | EXFILTRATION_PREVENTION | Bloquear Egresso, Capturar Tráfego, DLP, Isolamento |
| **nikto** | WEB_SCANNER_DEFENSE | WAF Rules, Rate Limit, Fake Responses, Assinar Scanner |
| **gobuster** | DIR_ENUM_DEFENSE | Servir 404 Fake, Gerar Honeypot Dirs, Log Padrões |
| **dnsrecon** | DNS_ENUM_DEFENSE | DNSSEC, Restringir Queries, Subdominios Falsos |
| **dig_axfr** | ZONE_TRANSFER_CRITICAL | ⚠️ CRÍTICO - Desabilitar AXFR, Escalação de Incidente |
| **hping3** | UDP_AMPLIFICATION_DEFENSE | Filtrar Malformados, Rate Limit UDP, DDoS Protection |
| **implicit** | CREDENTIAL_ABUSE_DEFENSE | Rotação Forçada, MFA Enforcement, Lockout Policy |

### 4. **Resposta Escalável por Nível de Alerta**

Exemplo para **Reconhecimento (RECON)**:

```python
VERDE/AMARELO:
- ENABLE_DNS_SEC
- ROTATE_SERVICE_PORTS
- ENABLE_SERVICE_ENCRYPTION
- HIDE_SERVICE_BANNERS

VERMELHO/CRÍTICO (+ escalação):
- [...todas acima...]
- ENABLE_HONEYPOT
- ESCALATE_ALERT_TO_SOC
```

### 5. **Gravação Automática no Banco**

A resposta gerada é salva como um novo registro de **contra-ataque**:

```json
{
  "target_ip": "192.168.1.100",
  "target_service": "BLUE_TEAM_RESPONSE_RECON",
  "attack_type": "COUNTER_ATTACK_RECON",
  "attack_phase": "fase_resposta",
  "success": true,
  "payload": {
    "acoes": ["ENABLE_DNS_SEC", "ROTATE_SERVICE_PORTS", ...],
    "tipo_resposta": "RECON_HARDENING",
    "severidade": 1
  },
  "lesson_learned": "Sistema reagiu automaticamente a recon com contra-medidas ativas"
}
```

---

## Endpoints da API

### 1. **Salvar Ataque + Dispara Reação (Automático)**
```
POST /api/attack-history
Content-Type: application/json

{
  "target_ip": "192.168.1.100",
  "target_port": 80,
  "attack_type": "recon",
  "attack_phase": "fase_4",
  "success": true,
  ...
}

Response:
{
  "sucesso": true,
  "attack_id": 42,
  "blue_team_reaction": {
    "status": "REAÇÃO AUTOMÁTICA ACIONADA",
    "nivel_alerta": "AMARELO",
    "resposta_id": 43,
    "tipo_resposta": "RECON_HARDENING",
    "acoes_executadas": ["ENABLE_DNS_SEC", "ROTATE_SERVICE_PORTS", ...]
  }
}
```

### 2. **Disparar Reação Manual**
```
GET /api/engine/reacao?target_ip=192.168.1.100&attack_type=dnsrecon

Response:
{
  "sucesso": true,
  "alvo": "192.168.1.100",
  "nivel_alerta": "LARANJA",
  "resposta_gerada": {
    "tipo_resposta": "DNS_ENUM_DEFENSE",
    "acoes": ["ENABLE_DNSSEC", "RESTRICT_QUERY_SOURCES", ...],
    "severidade": 2
  },
  "attack_id_salvo": 44
}
```

### 3. **Obter Status de Alerta do Alvo**
```
GET /api/engine/status/192.168.1.100

Response:
{
  "sucesso": true,
  "alvo": "192.168.1.100",
  "nivel_alerta": "VERMELHO",
  "nivel_numerico": 3,
  "total_ataques_recentes": 8,
  "ataques_bem_sucedidos": 2,
  "taxa_sucesso": "25.0%",
  "ataques_historio": [...],
  "acoes_recomendadas": ["Isolamento imediato", "Captura de tráfego", "Incidente confirmado"]
}
```

### 4. **Obter Histórico de Reações**
```
GET /api/engine/historico-reacoes/192.168.1.100?limit=20

Response:
{
  "sucesso": true,
  "alvo": "192.168.1.100",
  "total_reacoes": 5,
  "reacoes": [
    {
      "timestamp": "2026-05-27T14:23:00",
      "tipo_ataque_recebido": "recon",
      "tipo_reacao": "RECON_HARDENING",
      "nivel_alerta": "AMARELO",
      "acoes_executadas": ["ENABLE_DNS_SEC", "ROTATE_SERVICE_PORTS", ...]
    },
    ...
  ]
}
```

---

## Exemplos de Cenários

### Cenário 1: Teste Progressivo contra Reconhecimento

**Hora 1**: Análise de DNS
```
1º Ataque: dnsrecon → Nível AMARELO → Resposta: DNSSEC ativado
```

**Hora 2**: Varredura adicional
```
2º Ataque: dnsrecon → Nível LARANJA (2 tentativas) → Resposta: Honeypot DNS + Subdominios Falsos
```

**Hora 3**: Terceira tentativa
```
3º Ataque: dnsrecon → Nível VERMELHO → Resposta: Escalação para SOC + Bloqueio de IP
```

### Cenário 2: Detecção de Zone Transfer (CRÍTICO)

```
Ataque: dig_axfr (AXFR mal-sucedido) 
→ Nível: CRÍTICO (transferência = exposição crítica)
→ Resposta:
  - Desabilitar AXFR imediatamente
  - Notificar administrador DNS
  - Capturar detalhes do atacante
  - Atualizar firewall
  - Escalação de incidente MÁXIMA
```

### Cenário 3: Exploração Detectada

```
Ataque: exploit (SQL Injection bem-sucedida)
→ Nível: CRÍTICO (exploração = invasão)
→ Resposta IMEDIATA:
  - Isolar sistema da rede
  - Capture memory dump
  - Auditoria completa ativada
  - Notificar Incident Response
  - Preservar evidências forenses
```

---

## Integração com Frontend

### No Dashboard (React)

Após o usuário clicar em "INICIAR OPERAÇÃO":

1. Frontend envia teste via `POST /api/attack-history`
2. Backend salva ataque + dispara Motor
3. Motor gera resposta automática
4. **ComboBoxAlvo se atualiza** com novo alvo/contra-reação no F5/refresh
5. Modal de Auditoria mostra ambos ataques (ofensivos + defensivos)

---

## Regras de Contra-Ataque Explicadas

### 🔴 CRÍTICO: Zone Transfer Detectado
**Por quê?** Exposição de toda a zona DNS = acesso direto à infraestrutura completa
**Ação:** Desabilitar AXFR, bloqueio imediato, investigação forense

### 🔴 CRÍTICO: Exploração Bem-Sucedida
**Por quê?** Execução de código = invasão confirmada
**Ação:** Isolamento, memory dump, escalação máxima

### 🟠 ALTO: Arquivo Sensível Exposto (.env)
**Por quê?** Credenciais e chaves de API comprometidas
**Ação:** Rotação de credenciais, MFA enforcement

### 🟡 MÉDIO: Enumeração Contínua
**Por quê?** Reconhecimento persistente = preparação para ataque
**Ação:** Honeypot ativado, redirecionamento para dados falsos

### 🟢 BAIXO: Tentativas Isoladas
**Por quê?** Pode ser teste legítimo de pentesting ou scanner aleatório
**Ação:** Monitoramento aumentado, logging detalhado

---

## Configurações e Extensões

### Adicionar Novo Tipo de Contra-Ataque

```python
def _contraataque_novo_tipo(self, target_ip: str, nivel_alerta: str) -> Dict:
    """Descrição do novo contra-ataque"""
    return {
        "tipo_resposta": "NOME_RESPONSE",
        "descricao": "Descrição",
        "acoes": ["ACAO_1", "ACAO_2", ...],
        "severidade": self.niveis_alerta[nivel_alerta],
        "impacto_esperado": "..."
    }

# Registrar no mapeamento
self.contraataques["novo_tipo"] = self._contraataque_novo_tipo
```

### Ajustar Regras de Nível de Alerta

Editar método `calcular_nivel_alerta()` em `engine.py` para alterar limites de ataques/tempo.

---

## Resumo Técnico

- **Linguagem:** Python 3.9+
- **Framework:** FastAPI + SQLAlchemy ORM
- **Banco de Dados:** SQLite
- **Padrão:** Strategy + Factory (Motor de Regras Determinístico)
- **Inteligência:** Baseada 100% em histórico de ataques + mapeamento de tipos
- **Reação:** Automática, instantânea, sem ML/IA (previsível e auditável)

---

## Integração no Fluxo de Competição

✅ **Time Vermelho (Red Team)** realiza teste de segurança  
✅ **Backend** registra teste e dispara Motor  
✅ **Motor** gera resposta agressiva automática  
✅ **Time Azul (Blue Team)** reage em tempo real com contra-medidas  
✅ **Frontend** exibe histórico completo (ofensivo + defensivo)  
✅ **Professor Kali** avalia estratégia geral de ataque/defesa  

**Resultado:** Dinâmica realística de competição entre escolas! 🎯
