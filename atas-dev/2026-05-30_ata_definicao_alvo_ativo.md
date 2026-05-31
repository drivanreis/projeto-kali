# ATA: Definição de Alvo (Ativo) - Conceitos Fundamentais

**Data:** 30 de maio de 2026  
**Participante:** Definição conceitual do sistema KALI-CORE  
**Assunto:** Registro formal da definição de "Alvo" ou "Ativo" para o projeto

---

## 📋 Sumário Executivo

Definição precisa e abrangente do conceito de "alvo" ou "ativo" no contexto do KALI-CORE. Este conceito é fundamental para delimitar o escopo de operações do sistema.

---

## 🎯 Definição de Alvo (Ativo)

Um **alvo** (ou **ativo**) é qualquer dispositivo, sistema, interface ou infraestrutura capaz de transmitir, receber ou intermediar dados através de algum meio de comunicação.

### Critérios de Identificação

#### 1. **Meios de Comunicação Suportados**

Um ativo pode comunicar-se através de qualquer um desses meios:

| Meio | Características | Exemplo |
|------|-----------------|---------|
| **Wi-Fi** | Wireless local, IEEE 802.11 | Router, notebooks, smartphones |
| **Ethernet** | Cabeado, Fast/Gigabit/10G | Computadores, servidores, impressoras |
| **Bluetooth** | Comunicação de curto alcance | Headsets, mice, tablets |
| **Rede Móvel** | SIM card, 4G/5G/LTE | Celulares, modems, IoT celular |
| **Satélite** | Comunicação orbital | Terminais de satélite, GPS receivers |
| **Infravermelho** | IR, comunicação visual | Controles remotos, IR beacons |
| **Rádio** | Frequências RF diversas | Walkie-talkies, módulos LoRa |
| **Fibra Óptica** | Alta velocidade, backbone | Links de datacenter, ISP backhaul |
| **Cabo Submarino** | Comunicação intercontinental | Backbone da internet |

#### 2. **Identificadores Únicos Necessários**

Um ativo pode ser identificado por qualquer um desses identificadores:

- **Endereço MAC** (Media Access Control) - 48 bits, formato XX:XX:XX:XX:XX:XX
- **Endereço IP** (Internet Protocol) - IPv4 (32 bits) ou IPv6 (128 bits)
- **IMEI** (International Mobile Equipment Identity) - Identificador de celulares/modems
- **Serial Number** - Número de série do hardware
- **UUID/GUID** - Identificadores únicos de software
- **Hardware ID** - Identificadores proprietários do fabricante

**Observação Crítica:** Um ativo continua sendo válido mesmo sem hostname ou SSID visível. A invisibilidade não invalida sua natureza de ativo.

#### 3. **Exemplos Concretos de Ativos**

**Categoria: Computação**
- Desktop computers
- Notebooks/laptops
- Servidores (físicos ou virtuais)
- Workstations de engenharia
- Mainframes

**Categoria: Mobilidade**
- Smartphones (iOS, Android, etc)
- Tablets
- Phablets
- Wearables (smartwatch, fitness trackers)

**Categoria: Rede & Infraestrutura**
- Roteadores (residential, enterprise)
- Switches gerenciados e não-gerenciados
- Firewalls
- Modems
- Access Points (APs)
- Bridges e hubs

**Categoria: Periféricos & Impressão**
- Impressoras de rede
- Scanners de rede
- Multifuncionais (print/copy/scan)
- Plotters
- Label makers conectadas

**Categoria: IoT & Automação**
- Tomadas inteligentes
- Lâmpadas inteligentes
- Termostatos conectados
- Módulos Sonoff
- Relés inteligentes
- Controladores de automação (PLCs)

**Categoria: Sensores & Monitoramento**
- Sensores de temperatura
- Sensores de umidade
- Sensores de movimento (PIR)
- Câmeras IP
- Microfones conectados
- Medidores inteligentes (energy, water, gas)

**Categoria: Equipamentos Embarcados & Silenciosos**
- Dispositivos com comunicação silenciosa (sem UI)
- Sistemas de controle industrial
- Equipamento médico conectado
- Sistemas de vigilância
- Equipamentos de rede de telecomunicações

---

## 🔬 Análise Técnica: Por que "Silencioso" não Desqualifica um Ativo

Um equipamento que não possui identificação amigável (hostname, SSII) ou que opera sem interface visível continua sendo um ativo porque:

1. **Camada 2 (Data Link):** Ainda possui MAC address registrado no ARP
2. **Camada 3 (Network):** Ainda responde a pings ARP, DHCP requests, DNS queries
3. **Camada 4+ (Transport/Application):** Pode abrir conexões, responder a port scans
4. **Signature:** Possui fingerprint único (TTL default, stack TCP/IP behavior, resposta a ICMP)

**Implicação:** O KALI-CORE **PODE** rastrear e auditar ativos silenciosos através de:
- ARP scanning (identificação L2)
- Netstat/netsh (identificação de conexões)
- TTL analysis (fingerprinting passivo)
- MAC address lookup (vendor identification)
- Comportamento de resposta a probes

---

## 🛡️ Implicações para o KALI-CORE

### Escopo de Operações
- Todo ativo identificável é um potencial alvo
- Operações podem cobrir qualquer dos 5 módulos core:
  - `recon.py` - Reconhecimento de ativos
  - `deep_packet.py` - Análise de tráfego
  - `monitor.py` - Monitoramento contínuo
  - `arsenal.py` - Exploração de vulnerabilidades
  - `engine.py` - Orquestração inteligente

### Banco de Dados
- Tabela `alvos` deve aceitar qualquer formato de IP/domínio/MAC
- `ConfigAtaque` adapta-se a protocolos específicos do ativo
- `HistoricoOperacoes` registra tentativas contra cada ativo

### Filtragem de Resultados
- Dashboard deve permitir filtrar por tipo de ativo
- Relatórios devem segregar por categoria (computação, IoT, rede, etc)
- Alertas devem considerar criticidade do ativo

---

## ✅ Checklist de Validação

- [x] Definição abrangente documentada
- [x] Critérios de identificação claros
- [x] Exemplos práticos inclusos
- [x] Implicações técnicas explicadas
- [x] Integração com banco de dados definida
- [ ] Testes de descoberta de ativos (atividade futura)
- [ ] Validação com ferramentas reais (nmap, arp-scan, etc) (atividade futura)

---

## 📚 Referências Internas

- `docs/PROJECT_MAP.md` - Seção "Definição de Alvo (Ativo)"
- `backend/core/recon.py` - Lógica de descoberta de ativos
- `backend/models.py` - Schema de dados para Alvos
- Tabela `alvos` no banco de dados SQLite

---

## 🔮 Próximos Passos

1. **Implementação:** Validar descoberta de ativos contra diferentes tipos
2. **Testes:** Criar fixtures com múltiplos tipos de ativos (real + mock)
3. **Dashboard:** Adicionar filtro "Tipo de Ativo" na UI
4. **Relatórios:** Incluir análise por categoria de ativo nos reports

---

**Assinado em:** 30 de maio de 2026  
**Status:** ✅ FORMALIZADO E INTEGRADO
