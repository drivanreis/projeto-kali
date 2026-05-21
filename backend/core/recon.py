#!/usr/bin/env python3
"""
MÓDULO RECON - KALI-CORE
Consolidação de 00_recon_master.py + caçador_de_banners.py
"""

import socket
import requests
import time
import threading
import subprocess
import json
from datetime import datetime
import os

class ReconModule:
    def __init__(self, target="138.122.82.214"):
        self.target = target
        self.running = False
        self.status = {
            'portas_abertas': [],
            'servidor_detectado': False,
            'tipo_servidor': 'Unknown',
            'ultima_verificacao': None,
            'total_scans': 0,
            'horarios_ativo': []
        }
        
        # Portas críticas para pentest
        self.portas_criticas = [80, 443, 3389, 5900, 22, 21, 25, 53, 110, 143, 993, 995]
        
    def log(self, tipo, mensagem):
        """Log centralizado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [RECON-{tipo}] {mensagem}"
        
        # Salva no log central
        log_file = "data/reports/pentest.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(log_entry + "\n")
        
        print(log_entry)
        self.status['ultima_verificacao'] = timestamp
    
    def scan_portas_rapido(self):
        """Scan rápido de portas críticas"""
        self.log("SCAN", f"Iniciando scan rápido em {self.target}")
        
        portas_abertas = []
        
        for porta in self.portas_criticas:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)  # Timeout rápido
                resultado = sock.connect_ex((self.target, porta))
                
                if resultado == 0:
                    portas_abertas.append(porta)
                    self.log("PORTA", f"Porta {porta} aberta")
                
                sock.close()
                
            except Exception as e:
                continue
        
        self.status['portas_abertas'] = portas_abertas
        self.status['total_scans'] += 1
        
        if portas_abertas:
            self.log("SCAN", f"Portas abertas: {portas_abertas}")
        else:
            self.log("SCAN", "Nenhuma porta aberta detectada")
        
        return portas_abertas
    
    def banner_grabbing_sutil(self):
        """Banner grabbing sutil (HEAD request)"""
        self.log("BANNER", "Executando banner grabbing sutil...")
        
        try:
            # Requisição HEAD para não gerar tráfego excessivo
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            
            response = requests.head(
                f"http://{self.target}",
                headers=headers,
                timeout=5,
                allow_redirects=False
            )
            
            status_code = response.status_code
            server = response.headers.get('Server', 'Unknown')
            
            self.status['servidor_detectado'] = True
            self.status['tipo_servidor'] = server
            
            # Registra horário de atividade
            self.status['horarios_ativo'].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            if status_code == 404:
                self.log("BANNER", f"✓ SERVIDOR ATIVO! 404 Not Found - {server}")
                return True
            elif status_code == 200:
                self.log("BANNER", f"✓ SERVIDOR ATIVO! 200 OK - {server}")
                return True
            else:
                self.log("BANNER", f"Status {status_code} - {server}")
                return False
                
        except requests.exceptions.Timeout:
            self.log("BANNER", "Timeout - firewall bloqueando")
            return False
        except requests.exceptions.ConnectionError:
            self.log("BANNER", "Connection Error - porta fechada")
            return False
        except Exception as e:
            self.log("ERRO", f"Erro no banner grabbing: {e}")
            return False
    
    def verificar_https(self):
        """Verifica HTTPS também"""
        try:
            response = requests.head(
                f"https://{self.target}",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=5,
                verify=False
            )
            
            if response.status_code in [200, 404]:
                server = response.headers.get('Server', 'Unknown')
                self.log("HTTPS", f"HTTPS ativo - {server}")
                return True
                
        except requests.exceptions.SSLError:
            self.log("HTTPS", "Erro SSL - certificado inválido")
        except requests.exceptions.Timeout:
            self.log("HTTPS", "HTTPS timeout")
        except:
            pass
        
        return False
    
    def scan_completo(self):
        """Scan completo (portas + banner)"""
        self.log("SCAN", "Iniciando scan completo...")
        
        # Banner grabbing primeiro (mais sutil)
        servidor_ativo = self.banner_grabbing_sutil()
        
        if servidor_ativo:
            # Se servidor ativo, verifica HTTPS
            self.verificar_https()
            
            # Scan de portas
            self.scan_portas_rapido()
            
            # Verifica serviços específicos
            self.verificar_servicos()
        
        return servidor_ativo
    
    def verificar_servicos(self):
        """Verifica serviços específicos baseados nas portas abertas"""
        portas_abertas = self.status['portas_abertas']
        
        for porta in portas_abertas:
            if porta == 80 or porta == 443:
                self.verificar_web_server(porta)
            elif porta == 3389:
                self.verificar_rdp()
            elif porta == 22:
                self.verificar_ssh()
            elif porta == 21:
                self.verificar_ftp()
    
    def verificar_web_server(self, porta):
        """Verifica servidor web"""
        protocolo = "https" if porta == 443 else "http"
        
        try:
            response = requests.get(
                f"{protocolo}://{self.target}:{porta}",
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'},
                verify=False
            )
            
            self.log("WEB", f"Servidor web ativo na porta {porta}")
            
            # Extrai título se possível
            if '<title>' in response.text:
                title = response.text.split('<title>')[1].split('</title>')[0]
                self.log("WEB", f"Título: {title}")
            
            # Procura por diretórios comuns
            diretorios = ['/admin', '/login', '/panel', '/dashboard', '/wp-admin']
            for dir in diretorios:
                try:
                    resp = requests.get(f"{protocolo}://{self.target}:{porta}{dir}", timeout=3)
                    if resp.status_code != 404:
                        self.log("WEB", f"Diretório encontrado: {dir} - Status: {resp.status_code}")
                except:
                    continue
                    
        except Exception as e:
            self.log("WEB", f"Erro ao verificar servidor web: {e}")
    
    def verificar_rdp(self):
        """Verifica RDP"""
        self.log("RDP", "Verificando porta RDP 3389")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.target, 3389))
            
            # Tenta ler banner RDP
            data = sock.recv(1024)
            if data:
                self.log("RDP", f"Banner RDP detectado: {data[:50]}")
            
            sock.close()
            
        except Exception as e:
            self.log("RDP", f"Erro ao verificar RDP: {e}")
    
    def verificar_ssh(self):
        """Verifica SSH"""
        self.log("SSH", "Verificando porta SSH 22")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.target, 22))
            
            data = sock.recv(1024).decode()
            if data:
                self.log("SSH", f"Banner SSH: {data.strip()}")
            
            sock.close()
            
        except Exception as e:
            self.log("SSH", f"Erro ao verificar SSH: {e}")
    
    def verificar_ftp(self):
        """Verifica FTP"""
        self.log("FTP", "Verificando porta FTP 21")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.target, 21))
            
            data = sock.recv(1024).decode()
            if data:
                self.log("FTP", f"Banner FTP: {data.strip()}")
            
            sock.close()
            
        except Exception as e:
            self.log("FTP", f"Erro ao verificar FTP: {e}")
    
    def monitorar_sutil(self):
        """Monitoramento sutil contínuo"""
        self.log("MONITOR", "Iniciando monitoramento sutil contínuo...")
        
        while self.running:
            try:
                # Banner grabbing a cada 30 segundos
                servidor_ativo = self.banner_grabbing_sutil()
                
                if servidor_ativo:
                    # Se detectou atividade, scan rápido
                    self.scan_portas_rapido()
                
                time.sleep(30)  # Espera 30 segundos
                
            except Exception as e:
                self.log("ERRO", f"Erro no monitoramento: {e}")
                time.sleep(30)
    
    def iniciar(self):
        """Inicia módulo de recon"""
        self.running = True
        self.log("INICIO", f"Módulo RECON iniciado para {self.target}")
        
        # Inicia monitoramento em thread separada
        monitor_thread = threading.Thread(target=self.monitorar_sutil)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def parar(self):
        """Para módulo de recon"""
        self.running = False
        self.log("FIM", "Módulo RECON encerrado")
    
    def get_status(self):
        """Retorna status atual"""
        return self.status.copy()
    
    def salvar_estado(self):
        """Salva estado atual"""
        estado_file = "data/reports/recon_state.json"
        os.makedirs(os.path.dirname(estado_file), exist_ok=True)
        
        with open(estado_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def carregar_estado(self):
        """Carrega estado salvo"""
        estado_file = "data/reports/recon_state.json"
        
        if os.path.exists(estado_file):
            try:
                with open(estado_file, 'r') as f:
                    self.status = json.load(f)
            except:
                pass

# Teste do módulo
if __name__ == "__main__":
    recon = ReconModule()
    recon.scan_completo()
    print(recon.get_status())
