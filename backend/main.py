#!/usr/bin/env python3
"""
ORQUESTRADOR PRINCIPAL - KALI-CORE (FastAPI)
Ponto único de entrada do sistema com API REST e WebSocket
"""

import os
import sys
import time
import threading
import signal
import json
import asyncio
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import psutil

# Adiciona diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

from recon import ReconModule
from monitor import MonitorModule
from deep_packet import DeepPacketModule
from arsenal import ArsenalModule

class KaliCoreOrchestrator:
    def __init__(self, target):
        if not target:
            raise ValueError("Alvo (target) é obrigatório para inicializar KaliCoreOrchestrator")
        self.target = target
        self.running = True
        
        # Inicializa módulos
        self.recon_module = ReconModule(self.target)
        self.monitor_module = MonitorModule(self.target)
        self.deep_packet_module = DeepPacketModule(self.target)
        self.arsenal_module = ArsenalModule(self.target)
        self.dashboard = DashboardKali()

        # Threads dos módulos
        self.recon_thread = None
        self.monitor_threads = []
        self.deep_packet_thread = None
        self.arsenal_thread = None
        self.dashboard_thread = None
        
        # Configura handlers de sinal
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handler para sinais de encerramento"""
        print(f"\nRecebido sinal {signum}. Encerrando sistema...")
        self.running = False
        self.encerrar_modulos()
        sys.exit(0)
    
    def log(self, tipo, mensagem):
        """Log central do orquestrador"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [ORCHESTRATOR-{tipo}] {mensagem}"
        
        # Salva no log central
        log_file = "data/reports/pentest.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(log_entry + "\n")
        
        print(log_entry)
    
    def carregar_estados_iniciais(self):
        """Carrega estados salvos dos módulos"""
        self.log("INICIO", "Carregando estados iniciais...")

        self.recon_module.carregar_estado()
        self.monitor_module.carregar_estado()
        self.deep_packet_module.carregar_estado()
        self.arsenal_module.carregar_estado()

        self.log("INICIO", "Estados carregados com sucesso")
    
    def iniciar_modulos(self):
        """Inicia todos os módulos"""
        self.log("INICIO", "Iniciando módulos do KALI-CORE...")
        
        # Inicia módulo RECON
        self.recon_thread = self.recon_module.iniciar()
        self.log("INICIO", "Módulo RECON iniciado")
        
        # Inicia módulo MONITOR
        self.monitor_threads = self.monitor_module.iniciar()
        self.log("INICIO", f"Módulo MONITOR iniciado ({len(self.monitor_threads)} threads)")
        
        # Aguarda um pouco para os módulos estabilizarem
        time.sleep(2)
        
        # Inicia Dashboard
        self.iniciar_dashboard()
    
    def iniciar_dashboard(self):
        """Inicia dashboard em thread separada"""
        def dashboard_worker():
            try:
                self.dashboard.executar_dashboard()
            except Exception as e:
                self.log("ERRO", f"Erro no dashboard: {e}")
        
        self.dashboard_thread = threading.Thread(target=dashboard_worker)
        self.dashboard_thread.daemon = True
        self.dashboard_thread.start()
        
        self.log("INICIO", "Dashboard iniciado")
    
    def verificar_sugestao_deep_packet(self):
        """Verifica se deve iniciar automaticamente o Deep Packet"""
        deep_packet_iniciado = False

        while self.running:
            try:
                # Verifica status do recon a cada 30 segundos
                recon_status = self.recon_module.get_status()

                # Gatilho: porta 80 ou 443 aberta, ou servidor detectado com 404
                portas_abertas = recon_status.get('portas_abertas', [])
                servidor_detectado = recon_status.get('servidor_detectado', False)
                tipo_servidor = recon_status.get('tipo_servidor', 'Unknown')

                gatilho_acionado = (
                    (80 in portas_abertas or 443 in portas_abertas) or
                    (servidor_detectado and '404' in str(tipo_servidor))
                )

                if gatilho_acionado and not deep_packet_iniciado:
                    # Inicia automaticamente o Deep Packet
                    self.log(
                        "DEEP_PACKET",
                        "Gatilho acionado! Iniciando análise Deep Packet automaticamente"
                    )

                    # Salva sugestão para o dashboard
                    sugestao_file = "data/reports/deep_packet_sugestao.json"
                    os.makedirs(os.path.dirname(sugestao_file), exist_ok=True)

                    with open(sugestao_file, 'w') as f:
                        json.dump({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'motivo': 'Gatilho automático: porta 80/443 ou 404 detectado',
                            'tipo_servidor': tipo_servidor,
                            'portas_abertas': portas_abertas
                        }, f, indent=2)

                    # Inicia o módulo Deep Packet
                    self.deep_packet_thread = self.deep_packet_module.iniciar()
                    deep_packet_iniciado = True

                    # Aguarda 5 minutos antes de verificar novamente
                    time.sleep(300)
                elif not gatilho_acionado:
                    # Se não detectou, verifica a cada 30 segundos
                    time.sleep(30)
                else:
                    # Já iniciado, aguarda mais tempo
                    time.sleep(300)

            except Exception as e:
                self.log("ERRO", f"Erro na verificação de sugestão: {e}")
                time.sleep(30)

    def auto_invasao(self):
        """Função Auto-Invasão: detecta portas abertas e inicia arsenal"""
        arsenal_iniciado = False

        while self.running:
            try:
                # Verifica status do recon a cada 60 segundos
                recon_status = self.recon_module.get_status()
                portas_abertas = recon_status.get('portas_abertas', [])

                # Gatilho: porta 80 ou 443 aberta
                if (80 in portas_abertas or 443 in portas_abertas) and not arsenal_iniciado:
                    self.log(
                        "ARSENAL",
                        f"Portas web detectadas ({portas_abertas})! Iniciando Auto-Invasão..."
                    )

                    # FASE 1: Inteligência de Roteamento (ASN/WHOIS)
                    self.log("ARSENAL", "Fase 1: Inteligência de Roteamento")
                    whois_result = self.arsenal_module.whois_asn_lookup()

                    # FASE 2: Análise de Rota (CGNAT/MPLS)
                    self.log("ARSENAL", "Fase 2: Análise de Rota (CGNAT/MPLS)")
                    mtr_result = self.arsenal_module.mtr_trace_cgnat_mpls()

                    # Verifica se é CGNAT
                    if self.arsenal_module.status.get('cgnat_detectado'):
                        self.log("ARSENAL", "⚠️ CGNAT detectado! Iniciando IPv6 Enumeration")
                        ipv6_result = self.arsenal_module.ipv6_enumeration()

                    # FASE 3: DNS Brute Force Agressivo (AXFR falhou)
                    self.log("ARSENAL", "Fase 3: DNS Brute Force Agressivo")
                    dns_brute_result = self.arsenal_module.dns_brute_force_agressivo()

                    # FASE 4: Ataque BIND/DNS
                    self.log("ARSENAL", "Fase 4: Ataque BIND/DNS")
                    dnsrecon_result = self.arsenal_module.dnsrecon_scan()

                    # Tenta AXFR (Zone Transfer) - A BANDEIRA ESTÁ AQUI
                    axfr_result = self.arsenal_module.dig_axfr()

                    # FASE 5: Busca por Arquivos de Configuração Expostos
                    self.log("ARSENAL", "Fase 5: Busca por Arquivos de Configuração")
                    config_search_result = self.arsenal_module.buscar_arquivos_config_expostos()

                    # FASE 6: Auto-invasão web
                    self.log("ARSENAL", "Fase 6: Auto-invasão web")
                    resultados_web = self.arsenal_module.auto_invasao_web(portas_abertas)

                    # FASE 7: Teste UDP customizado (BIND)
                    self.log("ARSENAL", "Fase 7: Teste UDP customizado (BIND)")
                    hping3_result = self.arsenal_module.hping3_custom_udp(53)

                    # FASE 8: Análise de Entropia TLS
                    self.log("ARSENAL", "Fase 8: Análise de Entropia TLS")
                    tls_entropy_result = self.deep_packet_module.calcular_entropia_tls()

                    # Verifica se obteve provas de acesso
                    if resultados_web or axfr_result.get('axfr_success') or config_search_result.get('arquivos'):
                        self.log("ARSENAL", "Auto-Invasão concluída com resultados")

                        # Marca bandeira se encontrou vulnerabilidades
                        if 'nikto' in resultados_web and resultados_web['nikto'].get('vulnerabilidades'):
                            self.arsenal_module.marcar_bandeira(
                                "Vulnerabilidades web encontradas via NIKTO",
                                "nikto"
                            )

                        if 'gobuster_80' in resultados_web or 'gobuster_443' in resultados_web:
                            self.arsenal_module.marcar_bandeira(
                                "Diretórios enumerados via GOBUSTER",
                                "gobuster"
                            )

                    arsenal_iniciado = True

                    # Aguarda 10 minutos antes de verificar novamente
                    time.sleep(600)
                else:
                    # Se não detectou, verifica a cada 60 segundos
                    time.sleep(60)

            except Exception as e:
                self.log("ERRO", f"Erro na auto-invasão: {e}")
                time.sleep(60)
    
    def salvar_estados_periodicos(self):
        """Salva estados dos módulos periodicamente"""
        while self.running:
            try:
                # Salva estados a cada 2 minutos
                self.recon_module.salvar_estado()
                self.monitor_module.salvar_estado()
                self.deep_packet_module.salvar_estado()
                self.arsenal_module.salvar_estado()

                self.log("SALVAMENTO", "Estados dos módulos salvos")

                time.sleep(120)  # 2 minutos

            except Exception as e:
                self.log("ERRO", f"Erro ao salvar estados: {e}")
                time.sleep(60)
    
    def encerrar_modulos(self):
        """Encerra todos os módulos gracefulmente"""
        self.log("FIM", "Encerrando módulos do KALI-CORE...")

        # Para módulos
        if self.recon_module:
            self.recon_module.parar()

        if self.monitor_module:
            self.monitor_module.parar()

        if self.deep_packet_module:
            self.deep_packet_module.parar()

        if self.arsenal_module:
            self.arsenal_module.parar()

        # Salva estados finais
        try:
            self.recon_module.salvar_estado()
            self.monitor_module.salvar_estado()
            self.deep_packet_module.salvar_estado()
            self.arsenal_module.salvar_estado()
            self.log("FIM", "Estados finais salvos")
        except:
            pass

        self.log("FIM", "Sistema encerrado")
    
    def verificar_estrutura_diretorios(self):
        """Verifica se estrutura de diretórios existe"""
        diretorios_necessarios = [
            'core',
            'ui',
            'data/network',
            'data/reports',
            'archive'
        ]
        
        for diretorio in diretorios_necessarios:
            if not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
                self.log("ESTRUTURA", f"Diretório criado: {diretorio}")
    
    def mostrar_banner_inicial(self):
        """Mostra banner inicial do sistema"""
        print("="*80)
        print("KALI-CORE - SISTEMA UNIFICADO DE INTRUSÃO")
        print("="*80)
        print(f"ALVO: {self.target}")
        print(f"INÍCIO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print()
        print("Módulos sendo inicializados...")
        print("• RECON - Scan e banner grabbing")
        print("• MONITOR - Monitoramento contínuo")
        print("• ARSENAL - Orquestrador de ferramentas Kali")
        print("• DASHBOARD - Interface unificada")
        print()
    
    def executar(self):
        """Executa o orquestrador principal"""
        try:
            # Verifica estrutura
            self.verificar_estrutura_diretorios()
            
            # Mostra banner
            self.mostrar_banner_inicial()
            
            # Carrega estados
            self.carregar_estados_iniciais()
            
            # Inicia módulos
            self.iniciar_modulos()
            
            # Inicia thread de verificação de Deep Packet
            deep_packet_thread = threading.Thread(target=self.verificar_sugestao_deep_packet)
            deep_packet_thread.daemon = True
            deep_packet_thread.start()

            # Inicia thread de Auto-Invasão
            arsenal_thread = threading.Thread(target=self.auto_invasao)
            arsenal_thread.daemon = True
            arsenal_thread.start()

            # Inicia thread de salvamento periódico
            salvamento_thread = threading.Thread(target=self.salvar_estados_periodicos)
            salvamento_thread.daemon = True
            salvamento_thread.start()

            self.log("INICIO", "Sistema KALI-CORE totalmente operacional")
            
            # Mantém o orquestrador ativo
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("FIM", "Sistema interrompido pelo usuário")
        except Exception as e:
            self.log("ERRO", f"Erro fatal no orquestrador: {e}")
        finally:
            self.encerrar_modulos()

def main():
    """Função principal"""
    # Verifica se está executando como python3 main.py
    if len(sys.argv) > 0 and 'main.py' in sys.argv[0]:
        orchestrator = KaliCoreOrchestrator()
        orchestrator.executar()
    else:
        print("Execute: python3 main.py")

if __name__ == "__main__":
    main()
