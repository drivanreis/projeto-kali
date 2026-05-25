#!/usr/bin/env python3
"""
================================================================================
PROJETO KALI - OPERAÇÃO DEEP PACKET (MASTER RED)
FOCO: Descoberta de serviços atrás de Double NAT e identificação de túneis.
================================================================================
"""

import os
import subprocess
import os
import json
import threading
import time
import math
from datetime import datetime
import socket

class DeepPacketModule:
    def __init__(self, target):
        if not target:
            raise ValueError("Alvo (target) é obrigatório para inicializar DeepPacketModule")
        self.target = target
        self.relatorio_file = "estudo_nos_nat.txt"
        self.ttl_values = []
        self.ip_ids = []
        self.tunneis_detectados = []
        self.running = False
        self.status = {
            'ttl_analysis': {},
            'ip_id_analysis': {},
            'tunneis_detectados': [],
            'ultima_verificacao': None
        }
        
    def log_event(self, tipo, mensagem):
        """Registra eventos com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{tipo}] {mensagem}\n"
        
        with open(self.relatorio_file, 'a') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def analisar_ttl_fingerprinting(self):
        """Análise de saltos (TTL Fingerprinting)"""
        self.log_event("TTL", "Iniciando Análise de Saltos (TTL Fingerprinting)...")
        
        try:
            # Executa traceroute para analisar TTL
            result = subprocess.run(['traceroute', '-I', self.target], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                ttl_analysis = []
                
                for line in lines:
                    if 'ms' in line and not line.startswith('traceroute'):
                        # Extrai TTL e tempo
                        parts = line.split()
                        if len(parts) >= 3:
                            hop = parts[0]
                            # Procura por valores de tempo
                            for part in parts:
                                if 'ms' in part:
                                    try:
                                        ttl_value = float(part.replace('ms', ''))
                                    except ValueError:
                                        ttl_value = 0.0
                                    ttl_analysis.append({
                                        'hop': hop,
                                        'ttl': ttl_value,
                                        'timestamp': datetime.now().strftime("%H:%M:%S")
                                    })
                                    self.ttl_values.append(ttl_value)
                                    break
                
                # Analisa variação do TTL
                if len(ttl_analysis) > 2:
                    ttl_variance = max(self.ttl_values) - min(self.ttl_values)
                    
                    if ttl_variance > 10:
                        self.log_event("TTL", f"Alta variação detectada: {ttl_variance:.2f}ms - Possível balanceador/NAT complexo")
                    else:
                        self.log_event("TTL", f"Variação normal: {ttl_variance:.2f}ms - Rota estável")
                
                # Salva análise completa
                with open('ttl_analysis.json', 'w') as f:
                    json.dump(ttl_analysis, f, indent=2)
                
                self.log_event("TTL", f"Análise TTL concluída: {len(ttl_analysis)} hops analisados")
                
        except Exception as e:
            self.log_event("ERRO", f"Erro na análise TTL: {e}")
    
    def monitorar_tuneis_tshark(self):
        """Monitoramento de túneis com TShark (MPLS/GRE/AnyDesk/RDP)"""
        self.log_event("TSHARK", "Monitorando assinaturas de túneis (MPLS/GRE/AnyDesk/RDP)...")

        try:
            # Comando TShark para monitorar túneis e MPLS
            tshark_cmd = [
                'tshark', '-i', 'any', '-a', 'duration:300',
                '-f', f'host {self.target}',
                '-Y', 'tcp.flags.push == 1 or mpls or gre',
                '-T', 'fields',
                '-e', 'tcp.port',
                '-e', 'ip.dst',
                '-e', 'tcp.stream',
                '-e', 'frame.len',
                '-e', 'mpls.label',
                '-e', 'mpls.exp'
            ]

            process = subprocess.Popen(tshark_cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)

            stream_analysis = {}
            mpls_detected = False
            gre_detected = False

            while self.running:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break

                    parts = line.strip().split('\t')
                    if len(parts) >= 4:
                        port = parts[0]
                        dst = parts[1]
                        stream = parts[2]
                        frame_len = parts[3]

                        # Detecta MPLS labels
                        if len(parts) >= 5 and parts[4]:
                            mpls_label = parts[4]
                            if not mpls_detected:
                                self.log_event("MPLS", f"⚠️ MPLS LABEL DETECTADO: {mpls_label}")
                                self.status['mpls_detected'] = True
                                self.status['mpls_labels'] = []
                                mpls_detected = True
                            self.status['mpls_labels'].append(mpls_label)

                        # Detecta encapsulamento GRE
                        if 'gre' in line.lower():
                            if not gre_detected:
                                self.log_event("GRE", "⚠️ ENCAPSULAMENTO GRE DETECTADO")
                                self.status['gre_detected'] = True
                                gre_detected = True

                        # Analisa padrões de túnel
                        if self.is_tunnel_pattern(port, dst, frame_len):
                            if stream not in stream_analysis:
                                stream_analysis[stream] = {
                                    'port': port,
                                    'dst': dst,
                                    'packets': 0,
                                    'first_seen': datetime.now(),
                                    'last_seen': datetime.now(),
                                    'total_bytes': 0
                                }

                            stream_analysis[stream]['packets'] += 1
                            stream_analysis[stream]['last_seen'] = datetime.now()
                            stream_analysis[stream]['total_bytes'] += int(frame_len)
                            
                            # Detecta sessões longas (possível acesso remoto)
                            duration = (datetime.now() - stream_analysis[stream]['first_seen']).seconds
                            if duration > 60 and stream_analysis[stream]['packets'] > 10:
                                self.log_event("TUNNEL", 
                                    f"Sessão longa detectada: {dst}:{port} - {duration}s - {stream_analysis[stream]['packets']} pacotes")
                                
                                self.tunneis_detectados.append({
                                    'dst': dst,
                                    'port': port,
                                    'duration': duration,
                                    'packets': stream_analysis[stream]['packets'],
                                    'type': self.identify_tunnel_type(port)
                                })
                
                except Exception as e:
                    continue
            
            # Salva análise de streams
            with open('tunnel_analysis.json', 'w') as f:
                json.dump(stream_analysis, f, indent=2, default=str)
                
            self.log_event("TSHARK", f"Monitoramento TShark concluído: {len(stream_analysis)} streams analisados")
            
        except Exception as e:
            self.log_event("ERRO", f"Erro no TShark: {e}")
            # Fallback para monitoramento passivo
            self.monitoramento_passivo_fallback()
    
    def calcular_entropia_tls(self) -> dict:
        """Analisa entropia dos pacotes TLS na porta 443."""
        self.log_event("TLS_ENTROPY", "Iniciando análise de entropia TLS na porta 443")

        try:
            # Captura pacotes TLS com TShark
            tshark_cmd = [
                'tshark', '-i', 'any', '-a', 'duration:60',
                '-f', f'host {self.target} and port 443',
                '-Y', 'tls',
                '-T', 'fields',
                '-e', 'frame.len',
                '-e', 'tls.record.content_type'
            ]

            process = subprocess.Popen(tshark_cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)

            frame_lengths = []
            content_types = []

            while self.running:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break

                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        frame_len = parts[0]
                        content_type = parts[1]

                        if frame_len:
                            frame_lengths.append(int(frame_len))
                        if content_type:
                            content_types.append(content_type)

                except Exception:
                    continue

            # Calcula entropia dos tamanhos de frame
            if len(frame_lengths) > 10:
                entropy = self.calcular_entropia_shannon(frame_lengths)
                self.log_event("TLS_ENTROPY", f"Entropia TLS calculada: {entropy:.4f}")

                # Entropia baixa pode indicar tráfego TLS vulnerável
                if entropy < 3.0:
                    self.log_event("TLS_ENTROPY", "⚠️ ENTROPIA BAIXA DETECTADA - Possível TLS vulnerável")
                    self.status['tls_vulneravel'] = True
                    self.status['tls_entropy'] = entropy
                    return {
                        'sucesso': True,
                        'entropy': entropy,
                        'vulneravel': True,
                        'vetor_sugerido': 'TLS Downgrade Attack ou Cipher Suite Weakness'
                    }
                else:
                    self.log_event("TLS_ENTROPY", "✅ Entropia normal - TLS parece seguro")
                    self.status['tls_vulneravel'] = False
                    self.status['tls_entropy'] = entropy
                    return {
                        'sucesso': True,
                        'entropy': entropy,
                        'vulneravel': False
                    }
            else:
                self.log_event("TLS_ENTROPY", "Pacotes insuficientes para análise")
                return {'error': 'Pacotes insuficientes'}

        except Exception as e:
            self.log_event("TLS_ENTROPY", f"Erro: {e}")
            return {'error': str(e)}

    def calcular_entropia_shannon(self, data: list[int]) -> float:
        """Calcula entropia de Shannon para uma lista de dados."""
        if not data:
            return 0.0

        # Conta frequência de cada valor
        freq = {}
        for valor in data:
            freq[valor] = freq.get(valor, 0) + 1

        # Calcula entropia
        entropy = 0.0
        total = len(data)

        for count in freq.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def is_tunnel_pattern(self, port, dst, frame_len):
        """Identifica padrões de túnel"""
        # Portas comuns de acesso remoto
        remote_ports = ['6568', '7070', '3389', '5900', '443', '80']
        
        # Portas altas (possível túnel dinâmico)
        if port.isdigit() and int(port) > 10000:
            return True
        
        # Portas conhecidas de acesso remoto
        if port in remote_ports:
            return True
        
        # Pacotes pequenos e persistentes (keep-alive)
        if int(frame_len) < 100:
            return True
        
        return False
    
    def identify_tunnel_type(self, port):
        """Identifica tipo de túnel baseado na porta"""
        tunnel_types = {
            '6568': 'AnyDesk',
            '7070': 'AnyDesk Alt',
            '3389': 'RDP',
            '5900': 'VNC',
            '443': 'HTTPS Tunnel',
            '80': 'HTTP Tunnel'
        }
        
        return tunnel_types.get(port, 'Unknown')
    
    def tcp_ack_scan(self):
        """TCP ACK Scan para mapear portas filtradas"""
        self.log_event("NMAP", "Executando TCP ACK Scan para mapear portas filtradas pelo NAT...")
        
        try:
            # Executa TCP ACK Scan
            cmd = ['nmap', '-sA', '-p', '1000-40000', '--open', self.target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                filtered_ports = []
                unfiltered_ports = []
                
                for line in lines:
                    if 'filtered' in line:
                        # Extrai porta
                        port_match = re.search(r'(\d+)/tcp\s+filtered', line)
                        if port_match:
                            filtered_ports.append(port_match.group(1))
                    elif 'unfiltered' in line:
                        port_match = re.search(r'(\d+)/tcp\s+unfiltered', line)
                        if port_match:
                            unfiltered_ports.append(port_match.group(1))
                
                self.log_event("NMAP", f"Portas filtradas: {len(filtered_ports)}")
                self.log_event("NMAP", f"Portas não filtradas: {len(unfiltered_ports)}")
                
                # Analisa padrões de filtragem
                if len(filtered_ports) > 1000:
                    self.log_event("NMAP", "Alta filtragem detectada - Possível firewall/NAT restritivo")
                
                # Salva resultados
                scan_results = {
                    'filtered_ports': filtered_ports,
                    'unfiltered_ports': unfiltered_ports,
                    'scan_type': 'TCP ACK',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open('ack_scan_results.json', 'w') as f:
                    json.dump(scan_results, f, indent=2)
                
        except Exception as e:
            self.log_event("ERRO", f"Erro no TCP ACK Scan: {e}")
    
    def analisar_ip_id_nat(self):
        """Análise de IP ID para confirmar Double NAT"""
        self.log_event("IP_ID", "Analisando IP ID para confirmar Double NAT...")
        
        try:
            # Envia múltiplos pings e analisa IP ID
            ip_id_analysis = []
            
            for i in range(10):
                try:
                    result = subprocess.run(['ping', '-c', '1', self.target], 
                                          capture_output=True, text=True, timeout=5)
                    
                    if result.returncode == 0:
                        # Extrai IP ID do ping (se disponível)
                        ip_id_match = re.search(r'ip id=(\d+)', result.stderr.lower())
                        if ip_id_match:
                            ip_id = int(ip_id_match.group(1))
                            ip_id_analysis.append({
                                'sequence': i,
                                'ip_id': ip_id,
                                'timestamp': datetime.now().strftime("%H:%M:%S")
                            })
                            self.ip_ids.append(ip_id)
                    
                    time.sleep(1)
                    
                except Exception as e:
                    continue
            
            # Analisa sequencialidade dos IP IDs
            if len(ip_id_analysis) > 3:
                # Verifica se os IP IDs são sequenciais
                sequential = True
                for i in range(1, len(ip_id_analysis)):
                    expected_id = ip_id_analysis[i-1]['ip_id'] + 1
                    if ip_id_analysis[i]['ip_id'] != expected_id:
                        sequential = False
                        break
                
                if not sequential:
                    self.log_event("IP_ID", "IP IDs não sequenciais - Double NAT confirmado!")
                    
                    # Calcula variação
                    id_variance = max(self.ip_ids) - min(self.ip_ids)
                    self.log_event("IP_ID", f"Variação de IP ID: {id_variance} - Múltiplas máquinas redirecionando")
                else:
                    self.log_event("IP_ID", "IP IDs sequenciais - Possível single NAT")
                
                # Salva análise
                with open('ip_id_analysis.json', 'w') as f:
                    json.dump(ip_id_analysis, f, indent=2)
        
        except Exception as e:
            self.log_event("ERRO", f"Erro na análise de IP ID: {e}")
    
    def monitorar_keep_alive(self):
        """Monitora keep-alive de acessos remotos"""
        self.log_event("KEEPALIVE", "Monitorando keep-alive de acessos remotos...")
        
        # IPs conhecidos de serviços de acesso remoto
        remote_servers = [
            # AnyDesk
            '52.29.249.231',
            '52.28.33.241',
            '52.57.237.241',
            # TeamViewer
            '178.77.120.50',
            '109.239.140.10',
            # Chrome Remote Desktop
            '172.217.16.78',
            '142.250.184.78'
        ]
        
        keep_alive_patterns = {}
        
        while self.running:
            try:
                # Verifica conexões ativas para servidores remotos
                result = subprocess.run(['netstat', '-tn'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        if 'ESTABLISHED' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                dst = parts[4].split(':')[0]
                                
                                # Verifica se é conexão para servidor remoto
                                if dst in remote_servers:
                                    if dst not in keep_alive_patterns:
                                        keep_alive_patterns[dst] = {
                                            'first_seen': datetime.now(),
                                            'last_seen': datetime.now(),
                                            'packet_count': 0,
                                            'service': self.identify_service(dst)
                                        }
                                    
                                    keep_alive_patterns[dst]['last_seen'] = datetime.now()
                                    keep_alive_patterns[dst]['packet_count'] += 1
                                    
                                    # Detecta padrão de keep-alive
                                    duration = (datetime.now() - keep_alive_patterns[dst]['first_seen']).seconds
                                    if duration > 300 and keep_alive_patterns[dst]['packet_count'] > 60:
                                        self.log_event("KEEPALIVE", 
                                            f"Keep-alive detectado: {dst} - {keep_alive_patterns[dst]['service']} - {duration}s")
                
                time.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                self.log_event("ERRO", f"Erro no monitoramento keep-alive: {e}")
                time.sleep(30)
    
    def identify_service(self, ip):
        """Identifica serviço baseado no IP"""
        service_map = {
            '52.29.249.231': 'AnyDesk EU',
            '52.28.33.241': 'AnyDesk EU',
            '52.57.237.241': 'AnyDesk EU',
            '178.77.120.50': 'TeamViewer EU',
            '109.239.140.10': 'TeamViewer EU',
            '172.217.16.78': 'Chrome Remote Desktop',
            '142.250.184.78': 'Chrome Remote Desktop'
        }
        
        return service_map.get(ip, 'Unknown Remote Service')
    
    def monitoramento_passivo_fallback(self):
        """Fallback para monitoramento passivo"""
        self.log_event("FALLBACK", "Usando monitoramento passivo fallback...")
        
        while self.running:
            try:
                # Verifica conexões ativas
                result = subprocess.run(['netstat', '-tn'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        if 'ESTABLISHED' in line and self.target in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                dst = parts[4]
                                self.log_event("CONEXAO", f"Conexão ativa: {dst}")
                
                time.sleep(10)
                
            except Exception as e:
                time.sleep(10)
    
    def gerar_relatorio_final(self):
        """Gera relatório completo da análise"""
        relatorio = {
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'alvo': self.target,
            'ttl_analysis': {
                'valores': self.ttl_values,
                'variancia': max(self.ttl_values) - min(self.ttl_values) if self.ttl_values else 0
            },
            'ip_id_analysis': {
                'valores': self.ip_ids,
                'sequencial': len(self.ip_ids) > 0 and max(self.ip_ids) - min(self.ip_ids) == len(self.ip_ids) - 1
            },
            'tunneis_detectados': self.tunneis_detectados,
            'conclusoes': self.gerar_conclusoes()
        }
        
        with open('deep_packet_analysis.json', 'w') as f:
            json.dump(relatorio, f, indent=2)
        
        self.log_event("RELATORIO", f"Relatório completo gerado: {len(self.tunneis_detectados)} túneis detectados")
    
    def gerar_conclusoes(self):
        """Gera conclusões da análise"""
        conclusoes = []
        
        # Análise TTL
        if len(self.ttl_values) > 2:
            ttl_variance = max(self.ttl_values) - min(self.ttl_values)
            if ttl_variance > 10:
                conclusoes.append("Alta variação de TTL detectada - Possível balanceador de carga/NAT complexo")
        
        # Análise IP ID
        if len(self.ip_ids) > 3:
            sequential = True
            for i in range(1, len(self.ip_ids)):
                if self.ip_ids[i] != self.ip_ids[i-1] + 1:
                    sequential = False
                    break
            
            if not sequential:
                conclusoes.append("IP IDs não sequenciais - Double NAT confirmado")
            else:
                conclusoes.append("IP IDs sequenciais - Single NAT provável")
        
        # Túneis detectados
        if self.tunneis_detectados:
            conclusoes.append(f"{len(self.tunneis_detectados)} túneis de acesso remoto detectados")
        else:
            conclusoes.append("Nenhum túnel de acesso remoto detectado")
        
        return conclusoes
    
    def executar_analise_completa(self):
        """Executa análise completa"""
        self.log_event("INICIO", "Operação Deep Packet iniciada")
        
        try:
            # Fase 1: Análise TTL
            self.analisar_ttl_fingerprinting()
            
            # Fase 2: TCP ACK Scan
            self.tcp_ack_scan()
            
            # Fase 3: Análise IP ID
            self.analisar_ip_id_nat()
            
            # Fase 4: Monitoramento de túneis (paralelo)
            tunnel_thread = threading.Thread(target=self.monitorar_tuneis_tshark)
            tunnel_thread.daemon = True
            tunnel_thread.start()
            
            # Fase 5: Monitoramento keep-alive (paralelo)
            keepalive_thread = threading.Thread(target=self.monitorar_keep_alive)
            keepalive_thread.daemon = True
            keepalive_thread.start()
            
            # Mantém análise por tempo determinado
            time.sleep(600)  # 10 minutos
            
            self.running = False
            
            # Gera relatório final
            self.gerar_relatorio_final()
            
        except KeyboardInterrupt:
            self.running = False
            self.log_event("FIM", "Análise interrompida pelo operador")
            self.gerar_relatorio_final()

    def iniciar(self):
        """Inicia módulo de deep packet analysis"""
        self.running = True
        self.log_event("INICIO", f"Módulo DEEP PACKET iniciado para {self.target}")
        
        # Inicia análise em thread separada
        analysis_thread = threading.Thread(target=self.executar_analise_completa)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return analysis_thread
    
    def parar(self):
        """Para módulo de deep packet analysis"""
        self.running = False
        self.log_event("FIM", "Módulo DEEP PACKET encerrado")
    
    def get_status(self):
        """Retorna status atual"""
        return self.status.copy()
    
    def salvar_estado(self):
        """Salva estado atual"""
        estado_file = "data/reports/deep_packet_state.json"
        os.makedirs(os.path.dirname(estado_file), exist_ok=True)
        
        with open(estado_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def carregar_estado(self):
        """Carrega estado salvo"""
        estado_file = "data/reports/deep_packet_state.json"
        
        if os.path.exists(estado_file):
            try:
                with open(estado_file, 'r') as f:
                    self.status = json.load(f)
            except:
                pass

def main():
    print("="*80)
    print("OPERAÇÃO DEEP PACKET - MASTER RED")
    print("Análise de Double NAT e Identificação de Túneis")
    print("="*80)
    
    analyzer = DeepPacketModule()
    
    try:
        analyzer.executar_analise_completa()
    except KeyboardInterrupt:
        print("\n[!] Análise interrompida")
    except Exception as e:
        print(f"\n[!] Erro fatal: {e}")

if __name__ == "__main__":
    main()
