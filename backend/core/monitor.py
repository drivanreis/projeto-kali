#!/usr/bin/env python3
"""
MÓDULO MONITOR - KALI-CORE
Consolidação de 01_sentinela.py + monitoramento_passivo_noturno.py + 02_alerta_bt.py
"""

import socket
import os
import time
import subprocess
import threading
import json
from datetime import datetime
import psutil

class MonitorModule:
    def __init__(self, target):
        if not target:
            raise ValueError("Alvo (target) é obrigatório para inicializar MonitorModule")
        self.target = target
        self.running = False
        self.status = {
            'sentinela_ativa': False,
            'portas_monitoradas': [443, 3389, 5900, 5901, 5902, 5903],
            'ultima_verificacao': None,
            'total_alertas': 0,
            'alertas_recentes': [],
            'conexao_ativa': False
        }
        
        # Portas críticas para monitoramento
        self.portas_criticas = [443, 3389, 5900, 5901, 5902, 5903, 22, 80, 21]
        
    def log(self, tipo, mensagem):
        """Log centralizado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [MONITOR-{tipo}] {mensagem}"
        
        # Salva no log central
        log_file = "data/reports/pentest.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(log_entry + "\n")
        
        print(log_entry)
        self.status['ultima_verificacao'] = timestamp
    
    def sentinela_ping(self):
        """Sentinela: monitoramento por ping"""
        self.log("SENTINELA", f"Iniciando sentinela ping para {self.target}")
        
        while self.running:
            try:
                # Ping silencioso
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', self.target],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    self.status['conexao_ativa'] = True
                    self.log("SENTINELA", "✓ Alvo responde ao ping")

                    # Se respondeu, verifica portas
                    self.verificar_portas_criticas()
                else:
                    self.status['conexao_ativa'] = False
                    self.log("SENTINELA", "✗ Alvo não responde ao ping - Tentando TCP-Ping porta 443")

                    # Fallback: TCP-Ping na porta 443
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        resultado = sock.connect_ex((self.target, 443))

                        if resultado == 0:
                            self.status['conexao_ativa'] = True
                            self.log("SENTINELA", "✓ TCP-Ping 443 bem-sucedido - Alvo ativo")
                            self.alerta_porta_aberta(443)
                        else:
                            self.log("SENTINELA", "✗ TCP-Ping 443 falhou - Alvo offline")

                        sock.close()
                    except Exception as tcp_e:
                        self.log("SENTINELA", f"✗ Erro no TCP-Ping: {tcp_e}")

                time.sleep(60)  # Verifica a cada minuto

            except Exception as e:
                self.log("ERRO", f"Erro na sentinela: {e}")
                time.sleep(60)
    
    def verificar_portas_criticas(self):
        """Verifica portas críticas quando alvo ativo"""
        self.log("PORTAS", "Verificando portas críticas...")
        
        portas_abertas = []
        
        for porta in self.portas_criticas:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                resultado = sock.connect_ex((self.target, porta))
                
                if resultado == 0:
                    portas_abertas.append(porta)
                    self.alerta_porta_aberta(porta)
                
                sock.close()
                
            except Exception as e:
                continue
        
        if portas_abertas:
            self.log("PORTAS", f"Portas abertas detectadas: {portas_abertas}")
    
    def alerta_porta_aberta(self, porta):
        """Alerta quando porta abre"""
        self.status['total_alertas'] += 1
        
        alerta_msg = f"🚨 PORTA {porta} ABERTA em {self.target}!"
        self.log("ALERTA", alerta_msg)
        
        # Alerta sonoro
        os.system('echo -e "\a"')
        
        # Notificação visual
        try:
            subprocess.run([
                'notify-send',
                'ALERTA KALI',
                f'Porta {porta} aberta em {self.target}'
            ], check=False)
        except:
            pass
        
        # Registra alerta recente
        self.status['alertas_recentes'].append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'porta': porta,
            'tipo': 'Porta Aberta'
        })
        
        # Mantém apenas últimos 10 alertas
        if len(self.status['alertas_recentes']) > 10:
            self.status['alertas_recentes'] = self.status['alertas_recentes'][-10:]
    
    def monitorar_conexoes_locais(self):
        """Monitora conexões locais para detectar atividade suspeita"""
        self.log("CONEXOES", "Iniciando monitoramento de conexões locais...")
        
        while self.running:
            try:
                # Verifica conexões estabelecidas
                result = subprocess.run(
                    ['netstat', '-tn'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        if 'ESTABLISHED' in line and self.target in line:
                            # Conexão ativa com o alvo
                            parts = line.split()
                            if len(parts) >= 5:
                                dst = parts[4]
                                self.log("CONEXAO", f"Conexão ativa detectada: {dst}")
                
                time.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                self.log("ERRO", f"Erro no monitoramento de conexões: {e}")
                time.sleep(30)
    
    def monitorar_processos_rede(self):
        """Monitora processos de rede"""
        self.log("PROCESSOS", "Iniciando monitoramento de processos de rede...")

        while self.running:
            try:
                # Lista processos que usam rede
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        connections = proc.connections()
                        if connections:
                            for conn in connections:
                                if conn.status == 'ESTABLISHED':
                                    if hasattr(conn, 'raddr') and conn.raddr:
                                        if self.target in str(conn.raddr.ip):
                                            self.log("PROCESSO",
                                                f"Processo {proc.info['name']} (PID: {proc.info['pid']}) conectado ao alvo")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                    except:
                        continue

                time.sleep(60)  # Verifica a cada minuto

            except Exception as e:
                self.log("ERRO", f"Erro no monitoramento de processos: {e}")
                time.sleep(60)
    
    def monitorar_recursos_sistema(self):
        """Monitora recursos do sistema"""
        self.log("RECURSOS", "Iniciando monitoramento de recursos...")
        
        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memória
                memory = psutil.virtual_memory()
                
                # Rede
                network = psutil.net_io_counters()
                
                # Alerta se CPU alta
                if cpu_percent > 80:
                    self.log("RECURSOS", f"⚠️ CPU alta: {cpu_percent:.1f}%")
                
                # Alerta se memória baixa
                if memory.percent > 80:
                    self.log("RECURSOS", f"⚠️ Memória alta: {memory.percent:.1f}%")
                
                time.sleep(120)  # Verifica a cada 2 minutos
                
            except Exception as e:
                self.log("ERRO", f"Erro no monitoramento de recursos: {e}")
                time.sleep(120)
    
    def scan_passivo_continuo(self):
        """Scan passivo contínuo (sem gerar tráfego)"""
        self.log("PASSIVO", "Iniciando scan passivo contínuo...")
        
        while self.running:
            try:
                # Verifica apenas se já há conexões estabelecidas
                result = subprocess.run(
                    ['netstat', '-an'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    # Procura por conexões com o alvo
                    conexoes_alvo = []
                    for line in lines:
                        if self.target in line and 'ESTABLISHED' in line:
                            conexoes_alvo.append(line)
                    
                    if conexoes_alvo:
                        self.log("PASSIVO", f"Detectadas {len(conexoes_alvo)} conexões ativas")
                
                time.sleep(45)  # Verifica a cada 45 segundos
                
            except Exception as e:
                self.log("ERRO", f"Erro no scan passivo: {e}")
                time.sleep(45)
    
    def iniciar(self):
        """Inicia módulo de monitoramento"""
        self.running = True
        self.status['sentinela_ativa'] = True
        self.log("INICIO", f"Módulo MONITOR iniciado para {self.target}")
        
        threads = []
        
        # Thread 1: Sentinela Ping
        sentinela_thread = threading.Thread(target=self.sentinela_ping)
        sentinela_thread.daemon = True
        sentinela_thread.start()
        threads.append(sentinela_thread)
        
        # Thread 2: Monitoramento de Conexões
        conexoes_thread = threading.Thread(target=self.monitorar_conexoes_locais)
        conexoes_thread.daemon = True
        conexoes_thread.start()
        threads.append(conexoes_thread)
        
        # Thread 3: Monitoramento de Processos
        processos_thread = threading.Thread(target=self.monitorar_processos_rede)
        processos_thread.daemon = True
        processos_thread.start()
        threads.append(processos_thread)
        
        # Thread 4: Recursos do Sistema
        recursos_thread = threading.Thread(target=self.monitorar_recursos_sistema)
        recursos_thread.daemon = True
        recursos_thread.start()
        threads.append(recursos_thread)
        
        # Thread 5: Scan Passivo
        passivo_thread = threading.Thread(target=self.scan_passivo_continuo)
        passivo_thread.daemon = True
        passivo_thread.start()
        threads.append(passivo_thread)
        
        return threads
    
    def parar(self):
        """Para módulo de monitoramento"""
        self.running = False
        self.status['sentinela_ativa'] = False
        self.log("FIM", "Módulo MONITOR encerrado")
    
    def get_status(self):
        """Retorna status atual"""
        return self.status.copy()
    
    def salvar_estado(self):
        """Salva estado atual"""
        estado_file = "data/reports/monitor_state.json"
        os.makedirs(os.path.dirname(estado_file), exist_ok=True)
        
        with open(estado_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def carregar_estado(self):
        """Carrega estado salvo"""
        estado_file = "data/reports/monitor_state.json"
        
        if os.path.exists(estado_file):
            try:
                with open(estado_file, 'r') as f:
                    self.status = json.load(f)
            except:
                pass

# Teste do módulo
if __name__ == "__main__":
    monitor = MonitorModule()
    
    # Teste rápido
    monitor.verificar_portas_criticas()
    print(monitor.get_status())
