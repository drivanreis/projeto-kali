#!/usr/bin/env python3
"""
MOTOR DE INFERÊNCIA E REAÇÃO - KALI-CORE
Sistema de resposta agressiva automática do Time Azul (Blue Team)
Implementa regras de contra-ataque determinísticas baseadas em histórico
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
import sys
import os

# Adiciona diretórios ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import DatabaseManager, AttackHistory

class EngineInferencia:
    """
    Motor de Inferência - Responsável por análise estratégica e reação automática
    Simula o comportamento do Time Azul (Defensive Response Team)
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializa o motor de inferência
        
        Args:
            db_manager: Instância do gerenciador de banco de dados
        """
        self.db = db_manager
        self.niveis_alerta = {
            "VERDE": 0,      # Sem ameaça
            "AMARELO": 1,    # Atividade suspeita
            "LARANJA": 2,    # Ameaça confirmada
            "VERMELHO": 3,   # Ataque ativo
            "CRÍTICO": 4     # Invasão em progresso
        }
        
        # Mapeamento de contra-ataques por tipo de teste
        self.contraataques = {
            "recon": self._contraataque_recon,
            "scan": self._contraataque_scan,
            "exploit": self._contraataque_exploit,
            "maint": self._contraataque_manutencao,
            "exfil": self._contraataque_exfiltacao,
            "nikto": self._contraataque_web_scanner,
            "gobuster": self._contraataque_directory_enum,
            "dnsrecon": self._contraataque_dns_enum,
            "dig_axfr": self._contraataque_zone_transfer,
            "hping3": self._contraataque_udp_packets,
            "implicit": self._contraataque_credenciais_padrao
        }
    
    def calcular_nivel_alerta(self, target_ip: str) -> str:
        """
        Calcula o nível de alerta para um alvo baseado no histórico de ataques
        
        Args:
            target_ip: IP do alvo
            
        Returns:
            Nível de alerta (VERDE, AMARELO, LARANJA, VERMELHO, CRÍTICO)
        """
        try:
            # Consulta histórico para o IP
            ataques = self.db.session.query(AttackHistory).filter(
                AttackHistory.target_ip == target_ip
            ).all()
            
            if not ataques:
                return "VERDE"
            
            # Contabiliza ataques bem-sucedidos nas últimas 24 horas
            ataques_recentes = [a for a in ataques 
                              if (datetime.now() - a.timestamp).total_seconds() < 86400]
            
            ataques_sucesso = sum(1 for a in ataques_recentes if a.success)
            
            # Regras de nível de alerta
            if len(ataques_recentes) == 0:
                return "VERDE"
            elif ataques_sucesso == 0 and len(ataques_recentes) <= 3:
                return "AMARELO"
            elif ataques_sucesso == 0 and len(ataques_recentes) > 3:
                return "LARANJA"
            elif ataques_sucesso > 0 and ataques_sucesso < 3:
                return "VERMELHO"
            else:  # Múltiplos ataques bem-sucedidos
                return "CRÍTICO"
                
        except Exception as e:
            print(f"[ENGINE] Erro ao calcular nível de alerta: {e}")
            return "VERDE"
    
    def _contraataque_recon(self, target_ip: str, nivel_alerta: str) -> Dict:
        """
        Contra-ataque para RECONHECIMENTO (RECON)
        Tática: Encriptação de DNS, mudança de configuração de serviço
        """
        actions = [
            "ENABLE_DNS_SEC",           # Ativar DNSSEC para validação
            "ROTATE_SERVICE_PORTS",     # Rotacionar portas de serviço
            "ENABLE_SERVICE_ENCRYPTION", # Forçar encriptação SSL/TLS
            "HIDE_SERVICE_BANNERS"      # Ocultar banners de serviço
        ]
        
        resposta = {
            "tipo_resposta": "RECON_HARDENING",
            "descricao": "Infraestrutura endurecida contra reconhecimento",
            "acoes": actions,
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Redução em 70% da efetividade de enumeração"
        }
        
        if nivel_alerta in ["VERMELHO", "CRÍTICO"]:
            resposta["acoes"].append("ENABLE_HONEYPOT")
            resposta["acoes"].append("ESCALATE_ALERT_TO_SOC")
        
        return resposta
    
    def _contraataque_scan(self, target_ip: str, nivel_alerta: str) -> Dict:
        """
        Contra-ataque para VARREDURA DE PORTAS (SCAN)
        Tática: Bloqueio de porta, modificação de firewall, redirecionamento
        """
        actions = [
            "BLOCK_SOURCE_IP",          # Bloquear IP de origem
            "ENABLE_RATE_LIMITING",     # Aplicar rate limiting
            "ROTATE_OPEN_PORTS",        # Rotacionar portas abertas
            "REDIRECT_TO_HONEYPOT"      # Redirecionar para honeypot
        ]
        
        resposta = {
            "tipo_resposta": "SCAN_DEFENSE",
            "descricao": "Defesa contra varredura de portas detectada",
            "acoes": actions,
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Bloqueio completo da varredura"
        }
        
        if nivel_alerta in ["LARANJA", "VERMELHO", "CRÍTICO"]:
            resposta["acoes"].append("ENABLE_IDS_SIGNATURES")
            resposta["acoes"].append("LOG_TO_SIEM")
        
        return resposta
    
    def _contraataque_exploit(self, target_ip: str, nivel_alerta: str) -> Dict:
        """
        Contra-ataque para EXPLORAÇÃO (EXPLOIT)
        Tática: Isolamento de sistema, snapshot de segurança, defesa incrementada
        """
        actions = [
            "ISOLATE_SYSTEM_NETWORK",   # Isolar sistema da rede
            "CAPTURE_MEMORY_DUMP",      # Capturar dump de memória
            "ENABLE_FULL_AUDIT_LOGGING", # Auditoria completa
            "ACTIVATE_DEFENSE_COUNTERMEASURES" # Contra-medidas ativas
        ]
        
        resposta = {
            "tipo_resposta": "EXPLOIT_RESPONSE",
            "descricao": "Resposta crítica a tentativa de exploração",
            "acoes": actions,
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Prevenção da execução de exploração"
        }
        
        # Sempre escala em caso de exploit
        resposta["acoes"].extend([
            "ESCALATE_TO_INCIDENT_RESPONSE",
            "NOTIFY_SECURITY_TEAM",
            "PRESERVE_FORENSIC_EVIDENCE"
        ])
        
        return resposta
    
    def _contraataque_manutencao(self, target_ip: str, nivel_alerta: str) -> Dict:
        """
        Contra-ataque para MANUTENÇÃO (MAINT) - Persistência e Lateral Movement
        Tática: Detecção de backdoors, verificação de integridade, isolamento
        """
        actions = [
            "SCAN_FOR_BACKDOORS",       # Escanear para backdoors
            "VERIFY_SYSTEM_INTEGRITY",  # Verificar integridade do sistema
            "CHECK_PERSISTENCE_MECHANISMS", # Verificar mecanismos de persistência
            "MONITOR_LATERAL_MOVEMENT"  # Monitorar movimento lateral
        ]
        
        resposta = {
            "tipo_resposta": "PERSISTENCE_DETECTION",
            "descricao": "Detecção de tentativa de persistência ou movimento lateral",
            "acoes": actions,
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Bloqueio de persistência e movimento lateral"
        }
        
        if nivel_alerta in ["VERMELHO", "CRÍTICO"]:
            resposta["acoes"].extend([
                "DISCONNECT_FROM_NETWORK",
                "INITIATE_FORENSIC_INVESTIGATION"
            ])
        
        return resposta
    
    def _contraataque_exfiltacao(self, target_ip: str, nivel_alerta: str) -> Dict:
        """
        Contra-ataque para EXFILTRAÇÃO (EXFIL)
        Tática: Bloqueio de saída, captura de tráfego, isolamento de rede
        """
        actions = [
            "BLOCK_EGRESS_TRAFFIC",     # Bloquear tráfego de saída
            "CAPTURE_NETWORK_TRAFFIC",  # Capturar tráfego para análise
            "ENABLE_DLPV (Data Loss Prevention)",  # Ativar DLP
            "ISOLATE_COMPROMISED_SEGMENT" # Isolar segmento comprometido
        ]
        
        resposta = {
            "tipo_resposta": "EXFILTRATION_PREVENTION",
            "descricao": "Bloqueio de tentativa de exfiltração de dados",
            "acoes": actions,
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "100% de prevenção de vazamento de dados"
        }
        
        # Sempre escala em caso de exfiltração
        resposta["acoes"].extend([
            "QUARANTINE_DATA",
            "ALERT_COMPLIANCE_OFFICER",
            "INITIATE_BREACH_INVESTIGATION"
        ])
        
        return resposta
    
    def _contraataque_web_scanner(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque para NIKTO (Web Scanner)"""
        return {
            "tipo_resposta": "WEB_SCANNER_DEFENSE",
            "descricao": "Bloqueio de scanner web detectado (NIKTO)",
            "acoes": [
                "ENABLE_WAF_RULES",
                "RATE_LIMIT_REQUESTS",
                "SERVE_FAKE_RESPONSES",
                "LOG_SCANNER_SIGNATURES"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Scanner bloqueado e enegrecido com dados falsos"
        }
    
    def _contraataque_directory_enum(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque para GOBUSTER (Directory Enumeration)"""
        return {
            "tipo_resposta": "DIR_ENUM_DEFENSE",
            "descricao": "Bloqueio de enumeração de diretórios detectada (GOBUSTER)",
            "acoes": [
                "SERVE_404_FAKE_STRUCTURE",
                "GENERATE_HONEYPOT_DIRS",
                "LOG_ENUMERATION_PATTERNS",
                "BLOCK_PERSISTENT_SCANNERS"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Enumerador redirecionado para diretórios falsos"
        }
    
    def _contraataque_dns_enum(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque para DNSRECON (DNS Enumeration)"""
        return {
            "tipo_resposta": "DNS_ENUM_DEFENSE",
            "descricao": "Bloqueio de enumeração DNS detectada (DNSRECON)",
            "acoes": [
                "ENABLE_DNSSEC",
                "RESTRICT_QUERY_SOURCES",
                "SERVE_FAKE_SUBDOMAINS",
                "LOG_DNS_PROBES"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Enumeração DNS frustrada com respostas falsas"
        }
    
    def _contraataque_zone_transfer(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque para DIG AXFR (Zone Transfer) - CRÍTICO"""
        return {
            "tipo_resposta": "ZONE_TRANSFER_CRITICAL",
            "descricao": "CRÍTICO - Transferência de zona detectada (AXFR)",
            "acoes": [
                "DISABLE_ZONE_TRANSFERS",
                "RESTRICT_AXFR_QUERIES",
                "NOTIFY_DNS_ADMINISTRATOR",
                "CAPTURE_ATTACKER_DETAILS",
                "UPDATE_FIREWALL_RULES",
                "ESCALATE_INCIDENT"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Acesso crítico bloqueado, investigação forense iniciada"
        }
    
    def _contraataque_udp_packets(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque para HPING3 (Custom UDP Packets)"""
        return {
            "tipo_resposta": "UDP_AMPLIFICATION_DEFENSE",
            "descricao": "Bloqueio de pacotes UDP customizados detectados (HPING3)",
            "acoes": [
                "FILTER_MALFORMED_PACKETS",
                "RESTRICT_UDP_RESPONSES",
                "ENABLE_DDoS_PROTECTION",
                "RATE_LIMIT_UDP_RESPONSES"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Prevenção de ataques DDoS por amplificação UDP"
        }
    
    def _contraataque_credenciais_padrao(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque para IMPLICIT (Credenciais Padrão)"""
        return {
            "tipo_resposta": "CREDENTIAL_ABUSE_DEFENSE",
            "descricao": "Bloqueio de acesso com credenciais padrão/fraco detectado",
            "acoes": [
                "FORCE_CREDENTIAL_ROTATION",
                "IMPLEMENT_MFA",
                "MONITOR_FAILED_LOGINS",
                "TRIGGER_ACCOUNT_LOCKOUT_POLICY"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Credenciais padrão removidas, MFA enforçado"
        }
    
    def gerar_resposta_automatica(self, target_ip: str, attack_type: str) -> Dict:
        """
        Orquestra a geração de uma resposta automática agressiva
        
        Args:
            target_ip: IP do alvo
            attack_type: Tipo de ataque/teste recebido
            
        Returns:
            Dicionário com detalhes da resposta gerada
        """
        try:
            # Normaliza tipo de ataque
            attack_type_norm = attack_type.lower().strip()
            
            # Calcula nível de alerta
            nivel_alerta = self.calcular_nivel_alerta(target_ip)
            print(f"[ENGINE] Nível de alerta para {target_ip}: {nivel_alerta}")
            
            # Seleciona função de contra-ataque
            contraataque_func = self.contraataques.get(
                attack_type_norm,
                self._contraataque_generico
            )
            
            # Gera resposta
            resposta = contraataque_func(target_ip, nivel_alerta)
            
            return {
                "sucesso": True,
                "timestamp": datetime.now().isoformat(),
                "alvo_ip": target_ip,
                "tipo_teste": attack_type,
                "nivel_alerta": nivel_alerta,
                "resposta": resposta
            }
            
        except Exception as e:
            print(f"[ENGINE] Erro ao gerar resposta automática: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _contraataque_generico(self, target_ip: str, nivel_alerta: str) -> Dict:
        """Contra-ataque genérico para tipos não mapeados"""
        return {
            "tipo_resposta": "GENERIC_DEFENSE",
            "descricao": "Resposta defensiva genérica ativada",
            "acoes": [
                "ENABLE_MONITORING",
                "LOG_EVENT",
                "ALERT_SECURITY_TEAM"
            ],
            "severidade": self.niveis_alerta[nivel_alerta],
            "impacto_esperado": "Evento monitorado e registrado"
        }
    
    def salvar_resposta_como_ataque(self, target_ip: str, attack_type: str, 
                                   resposta_dict: Dict) -> Optional[int]:
        """
        Salva a resposta automática como um registro de ataque no banco
        Simula o "contra-ataque" do Time Azul
        
        Args:
            target_ip: IP do alvo
            attack_type: Tipo de ataque que foi recebido
            resposta_dict: Dicionário com dados da resposta
            
        Returns:
            ID do ataque salvo ou None em caso de erro
        """
        try:
            attack_data = {
                "target_ip": target_ip,
                "target_port": 0,  # Resposta contra-atacante é de nível sistema
                "target_service": f"BLUE_TEAM_RESPONSE_{attack_type}",
                "attack_phase": "fase_resposta",
                "attack_type": f"COUNTER_ATTACK_{attack_type.upper()}",
                "payload": json.dumps(resposta_dict.get("resposta", {})),
                "success": True,  # Resposta automática é sempre bem-sucedida
                "response_code": 200,
                "response_data": json.dumps({
                    "nivel_alerta": resposta_dict.get("nivel_alerta"),
                    "acoes_executadas": resposta_dict.get("resposta", {}).get("acoes", []),
                    "timestamp": resposta_dict.get("timestamp")
                }),
                "duration_ms": 50.0,  # Simulado
                "lesson_learned": f"Sistema reagiu automaticamente a {attack_type} com contra-medidas ativas",
                "confidence_score": 0.95
            }
            
            # Salva no banco de dados
            attack_id = self.db.save_attack(attack_data)
            
            print(f"[ENGINE] Resposta automática salva: ID {attack_id} para {target_ip}")
            return attack_id
            
        except Exception as e:
            print(f"[ENGINE] Erro ao salvar resposta automática: {e}")
            return None
    
    def processar_ataque_e_reagir(self, target_ip: str, attack_type: str) -> Dict:
        """
        Função completa: Recebe ataque, gera resposta e salva no banco
        
        Args:
            target_ip: IP do alvo
            attack_type: Tipo de ataque/teste
            
        Returns:
            Dicionário consolidado com resposta gerada e ID salvo
        """
        # Gera resposta automática
        resposta = self.gerar_resposta_automatica(target_ip, attack_type)
        
        if resposta.get("sucesso"):
            # Salva resposta como contra-ataque no banco
            attack_id = self.salvar_resposta_como_ataque(
                target_ip, 
                attack_type,
                resposta
            )
            resposta["attack_id_salvo"] = attack_id
        
        return resposta
