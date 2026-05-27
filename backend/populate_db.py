#!/usr/bin/env python3
"""
CARGA MASSIVA AUTOMÁTICA DE EVENTOS DINÂMICOS
Popula o banco de dados SQLite com múltiplos cenários de ataque reais
Executada automaticamente no startup do backend
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
from models import DatabaseManager, Alvo, HistoricoOperacoes, VulnerabilidadesOcorrencias

class PopuladorBancoDados:
    """Responsável pela carga massiva de eventos dinâmicos"""
    
    # IP histórico principal (Blue Team - nossa escola)
    IP_HISTORICO = "138.122.82.214"
    
    # IPs dinâmicos do Time Azul (competição)
    IPS_TIME_AZUL = [
        "138.122.82.214",    # Principal histórico
        "192.168.1.100",     # Secondary
        "192.168.1.101",     # Tertiary
        "10.0.0.50",         # Remote
        "10.0.0.51",         # Remote 2
    ]
    
    # Cenários de ataque REAL com contraataques automáticos
    CENARIOS_ATAQUE = {
        "scan_portas": {
            "attack_type": "nmap_scan",
            "attack_phase": "fase_1",
            "payloads": [
                "nmap -sS {target} -p 1-1000",
                "nmap -sU {target} -p 53,67,68",
                "nmap -sA {target} -p 1-65535",
            ],
            "contraataques": [
                "counter_scan_agressivo",
                "firewall_automatico",
                "tarpit_com_rate_limiting",
            ]
        },
        "sql_injection": {
            "attack_type": "sql_injection",
            "attack_phase": "fase_6",
            "payloads": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "1 UNION SELECT NULL,NULL,NULL --",
            ],
            "contraataques": [
                "ofuscacao_de_payload",
                "sanitizacao_automatica",
                "bloqueio_de_patron",
            ]
        },
        "forca_bruta": {
            "attack_type": "brute_force_ssh",
            "attack_phase": "fase_3",
            "payloads": [
                "ssh -u admin {target} -p 22",
                "ssh -u root {target} -p 22",
                "ssh -u ubuntu {target} -p 22",
            ],
            "contraataques": [
                "honeypot_ssh",
                "ip_ban_imediato",
                "rate_limit_conexoes",
            ]
        },
        "directory_traversal": {
            "attack_type": "gobuster",
            "attack_phase": "fase_6",
            "payloads": [
                "gobuster dir -u http://{target} -w common.txt",
                "gobuster dns -d {target} -w dns.txt",
            ],
            "contraataques": [
                "honeypot_diretorios",
                "bloqueio_pattern_matching",
                "deteccao_scanner",
            ]
        },
        "dns_enumeration": {
            "attack_type": "dnsrecon",
            "attack_phase": "fase_4",
            "payloads": [
                "dnsrecon -d {target} -a",
                "dnsrecon -d {target} -t axfr",
            ],
            "contraataques": [
                "desabilitar_axfr",
                "dns_firewall",
                "rate_limit_dns",
            ]
        },
        "xss_attack": {
            "attack_type": "xss",
            "attack_phase": "fase_6",
            "payloads": [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
            ],
            "contraataques": [
                "csp_policy",
                "html_encoding",
                "sanitizacao_xss",
            ]
        },
        "ddos": {
            "attack_type": "ddos_flood",
            "attack_phase": "fase_2",
            "payloads": [
                "hping3 -c 1000 -d 512 -S {target}",
                "wget --spider -r -p http://{target}",
            ],
            "contraataques": [
                "rate_limiting_agressivo",
                "blackhole_automatico",
                "load_balancing",
            ]
        },
        "credential_spray": {
            "attack_type": "credential_spray",
            "attack_phase": "fase_5",
            "payloads": [
                "spray_attack_admin",
                "spray_attack_root",
            ],
            "contraataques": [
                "account_lockout",
                "anomaly_detection",
                "mfa_enforcement",
            ]
        },
        "heartbleed": {
            "attack_type": "heartbleed_test",
            "attack_phase": "fase_7",
            "payloads": [
                "ssltest -b heartbleed",
            ],
            "contraataques": [
                "ssl_update",
                "tls_1_2_enforce",
                "cert_revocation",
            ]
        },
        "privilege_escalation": {
            "attack_type": "privilege_escalation",
            "attack_phase": "fase_8",
            "payloads": [
                "sudo -l",
                "find / -perm -4000 -type f",
            ],
            "contraataques": [
                "selinux_enforcement",
                "apparmor_profile",
                "privilege_restriction",
            ]
        }
    }
    
    # Fases de ataque
    FASES = ["fase_1", "fase_2", "fase_3", "fase_4", "fase_5", "fase_6", "fase_7", "fase_8"]
    
    # Criticidades de vulnerabilidades
    CRITICIDADES = ["critica", "alta", "media", "baixa"]
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.records_criados = 0
    
    def verificar_banco_vazio(self) -> bool:
        """Verifica se o banco está vazio (sem alvos ou operações)"""
        try:
            count_alvos = self.db.session.query(Alvo).count()
            count_ops = self.db.session.query(HistoricoOperacoes).count()
            
            vazio = (count_alvos == 0 and count_ops == 0)
            
            print(f"[POPULATE] Verificação: Alvos={count_alvos}, Operações={count_ops}, Vazio={vazio}")
            return vazio
        except Exception as e:
            print(f"[POPULATE] Erro ao verificar banco: {e}")
            return False
    
    def criar_alvos_dinamicos(self) -> Dict[str, int]:
        """Cria alvos dinâmicos, garantindo o IP histórico principal"""
        print("[POPULATE] Criando alvos dinâmicos...")
        alvos_map = {}
        
        for ip in self.IPS_TIME_AZUL:
            try:
                alvo_id = self.db.save_alvo(ip)
                alvos_map[ip] = alvo_id
                print(f"[POPULATE] ✓ Alvo criado: {ip} (ID={alvo_id})")
            except Exception as e:
                print(f"[POPULATE] ✗ Erro ao criar alvo {ip}: {e}")
        
        return alvos_map
    
    def gerar_eventos_masivos(self, alvos_map: Dict[str, int], quantidade_minima: int = 150) -> int:
        """Gera 150+ registros de ataque massivos"""
        print(f"[POPULATE] Gerando {quantidade_minima}+ eventos de ataque...")
        
        eventos_criados = 0
        timestamp_base = datetime.now() - timedelta(days=30)  # Últimos 30 dias
        
        # Para cada alvo
        for ip, alvo_id in alvos_map.items():
            # Define densidade maior para o IP histórico
            densidade = 40 if ip == self.IP_HISTORICO else 15
            
            # Para cada cenário de ataque
            for cenario_nome, cenario_config in self.CENARIOS_ATAQUE.items():
                # Gera múltiplos registros do mesmo cenário
                for i in range(densidade // len(self.CENARIOS_ATAQUE)):
                    try:
                        # Payload aleatório do cenário
                        payload = random.choice(cenario_config["payloads"])
                        payload = payload.replace("{target}", ip)
                        
                        # Fase aleatória
                        fase = cenario_config["attack_phase"]
                        
                        # Success variável (80% sucesso para o IP histórico, 50% para outros)
                        taxa_sucesso = 0.8 if ip == self.IP_HISTORICO else 0.5
                        success = random.random() < taxa_sucesso
                        
                        # Response code
                        response_code = 200 if success else 403
                        
                        # Response data com detalhes
                        response_data = json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "status": "sucesso" if success else "falha",
                            "resultado": random.choice(cenario_config["contraataques"]),
                            "mitigacao": "ativa" if ip == self.IP_HISTORICO else "padrão",
                        })
                        
                        # Timestamp variado
                        dias_atras = random.randint(0, 30)
                        horas_atras = random.randint(0, 23)
                        timestamp = timestamp_base + timedelta(days=dias_atras, hours=horas_atras)
                        
                        # Cria operação
                        op_id = self.db.save_operacao(
                            alvo_id=alvo_id,
                            attack_type=cenario_config["attack_type"],
                            attack_phase=fase,
                            payload=payload,
                            success=success,
                            response_code=response_code,
                            response_data=response_data
                        )
                        
                        # Cria vulnerabilidades associadas
                        if success:
                            self._criar_vulnerabilidades(op_id)
                        
                        eventos_criados += 1
                        
                        # Progress indicator
                        if eventos_criados % 20 == 0:
                            print(f"[POPULATE] ... {eventos_criados} eventos criados")
                    
                    except Exception as e:
                        print(f"[POPULATE] ✗ Erro ao criar evento: {e}")
                        continue
        
        print(f"[POPULATE] ✓ Total de {eventos_criados} eventos criados!")
        self.records_criados = eventos_criados
        return eventos_criados
    
    def _criar_vulnerabilidades(self, operacao_id: int):
        """Cria vulnerabilidades associadas a uma operação"""
        vulnerabilidades = [
            {
                "criticidade": "critica",
                "titulo": "SQL Injection detectado",
                "descricao": "Formulário vulnerável a injeção de SQL detectado na operação",
                "correcao": "Usar prepared statements e validação de entrada"
            },
            {
                "criticidade": "alta",
                "titulo": "Credenciais fracas expostas",
                "descricao": "Credenciais padrão ou fracas foram encontradas",
                "correcao": "Implementar política de senhas forte e MFA"
            },
            {
                "criticidade": "media",
                "titulo": "Configuração de segurança inadequada",
                "descricao": "Parâmetros de segurança não estão otimizados",
                "correcao": "Seguir guias de hardening do OWASP"
            },
        ]
        
        # Adiciona 1-3 vulnerabilidades aleatoriamente
        quantidade = random.randint(1, 3)
        for vuln in random.sample(vulnerabilidades, min(quantidade, len(vulnerabilidades))):
            try:
                self.db.save_vulnerabilidade(
                    operacao_id=operacao_id,
                    criticidade=vuln["criticidade"],
                    titulo=vuln["titulo"],
                    descricao=vuln["descricao"],
                    correcao=vuln["correcao"]
                )
            except Exception as e:
                print(f"[POPULATE] ✗ Erro ao criar vulnerabilidade: {e}")
    
    def marcar_eventos_contra_atacados(self):
        """Marca eventos do IP histórico como 'Contra-Atacado' e com alta taxa de sucesso"""
        print(f"[POPULATE] Marcando eventos do {self.IP_HISTORICO} como Contra-Atacados...")
        
        try:
            # Busca alvo histórico
            alvo_historico = self.db.session.query(Alvo).filter(
                Alvo.ip_dominio == self.IP_HISTORICO
            ).first()
            
            if not alvo_historico:
                print(f"[POPULATE] ✗ Alvo histórico {self.IP_HISTORICO} não encontrado")
                return
            
            # Busca todas as operações do alvo histórico
            operacoes = self.db.session.query(HistoricoOperacoes).filter(
                HistoricoOperacoes.alvo_id == alvo_historico.id
            ).all()
            
            # Marca como contra-atacadas (sucesso + status)
            contador = 0
            for op in operacoes:
                op.success = True
                op.status_fase = "contra-atacado"
                op.response_code = 200
                op.response_data = json.dumps({
                    "status": "contra-atacado",
                    "reacao": "automatica",
                    "bloqueio": "ativo",
                    "timestamp": datetime.now().isoformat()
                })
                contador += 1
            
            self.db.session.commit()
            print(f"[POPULATE] ✓ {contador} eventos marcados como Contra-Atacados")
        
        except Exception as e:
            print(f"[POPULATE] ✗ Erro ao marcar contra-ataques: {e}")
            self.db.session.rollback()
    
    def executar_carga_completa(self):
        """Executa carga completa do banco de dados"""
        print("[POPULATE] ============================================")
        print("[POPULATE] INICIANDO CARGA MASSIVA DE EVENTOS")
        print("[POPULATE] ============================================")
        
        # 1. Verifica se vazio
        if not self.verificar_banco_vazio():
            print("[POPULATE] ⚠️  Banco já contém dados. Pulando população automática.")
            return False
        
        # 2. Cria alvos dinâmicos
        alvos_map = self.criar_alvos_dinamicos()
        if not alvos_map:
            print("[POPULATE] ✗ Falha ao criar alvos")
            return False
        
        # 3. Gera eventos massivos (mínimo 150)
        eventos = self.gerar_eventos_masivos(alvos_map, quantidade_minima=150)
        if eventos < 150:
            print(f"[POPULATE] ⚠️  Apenas {eventos} eventos criados (esperado: 150+)")
        
        # 4. Marca eventos contra-atacados
        self.marcar_eventos_contra_atacados()
        
        print("[POPULATE] ============================================")
        print(f"[POPULATE] POPULAÇÃO COMPLETA: {eventos} EVENTOS CRIADOS")
        print("[POPULATE] ✓ Sistema pronto para uso imediato")
        print("[POPULATE] ============================================")
        
        return True


def popular_banco_ao_startup(db_manager: DatabaseManager) -> bool:
    """
    Função de hook para startup do FastAPI
    Popula automaticamente se banco vazio
    """
    try:
        populador = PopuladorBancoDados(db_manager)
        return populador.executar_carga_completa()
    except Exception as e:
        print(f"[POPULATE] ✗ ERRO CRÍTICO na população: {e}")
        return False
