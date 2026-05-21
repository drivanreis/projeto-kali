#!/usr/bin/env python3
"""DASHBOARD UNIFICADO - KALI-CORE.

Interface principal do sistema.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any


class DashboardKali:
    """Dashboard unificado do sistema KALI-CORE.

    Exibe status dos módulos RECON, MONITOR e DEEP PACKET em tempo real.
    """

    def __init__(self) -> None:
        """Inicializa o dashboard."""
        self.running: bool = True
        self.recon_status: Dict[str, Any] = {}
        self.monitor_status: Dict[str, Any] = {}
        self.deep_packet_status: Dict[str, Any] = {}
        
    def limpar_tela(self) -> None:
        """Limpa a tela do terminal."""
        os.system("clear")
    
    def carregar_estados(self) -> None:
        """Carrega os estados dos módulos dos arquivos JSON."""
        try:
            if os.path.exists("data/reports/recon_state.json"):
                with open("data/reports/recon_state.json", "r") as f:
                    self.recon_status = json.load(f)

            if os.path.exists("data/reports/monitor_state.json"):
                with open("data/reports/monitor_state.json", "r") as f:
                    self.monitor_status = json.load(f)

            if os.path.exists("data/reports/deep_packet_state.json"):
                with open("data/reports/deep_packet_state.json", "r") as f:
                    self.deep_packet_status = json.load(f)
        except Exception:
            pass
    
    def desenhar_header(self) -> None:
        """Desenha o cabeçalho do dashboard."""
        agora = datetime.now().strftime("%H:%M:%S")

        print("=" * 80)
        print(f"{'DASHBOARD OPERAÇÃO KALI - KALI-CORE':^80}")
        print("=" * 80)
        print(f"{'ALVO: 138.122.82.214':^40} {'HORA: ' + agora:^40}")
        print("-" * 80)
    
    def desenhar_painel_recon(self) -> None:
        """Desenha o painel do módulo RECON."""
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│                    MÓDULO RECON                        │")
        print("├─────────────────────────────────────────────────────────────┤")

        if self.recon_status:
            servidor_detectado = self.recon_status.get("servidor_detectado", False)
            tipo_servidor = self.recon_status.get("tipo_servidor", "Unknown")
            portas_abertas = self.recon_status.get("portas_abertas", [])
            total_scans = self.recon_status.get("total_scans", 0)
            ultima_verificacao = self.recon_status.get("ultima_verificacao", "N/A")

            print(
                f"│ Servidor Detectado: "
                f"{'SIM' if servidor_detectado else 'NÃO':<35} │"
            )
            print(f"│ Tipo Servidor: {tipo_servidor:<40} │")
            print(f"│ Portas Abertas: {str(portas_abertas):<38} │")
            print(f"│ Total Scans: {total_scans:<42} │")
            print(f"│ Última Verificação: {ultima_verificacao:<30} │")
        else:
            print("│ Aguardando dados do módulo RECON...                    │")

        print("└─────────────────────────────────────────────────────────────┘")
    
    def desenhar_painel_monitor(self) -> None:
        """Desenha o painel do módulo MONITOR."""
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│                   MÓDULO MONITOR                       │")
        print("├─────────────────────────────────────────────────────────────┤")

        if self.monitor_status:
            sentinela_ativa = self.monitor_status.get("sentinela_ativa", False)
            conexao_ativa = self.monitor_status.get("conexao_ativa", False)
            total_alertas = self.monitor_status.get("total_alertas", 0)
            alertas_recentes = self.monitor_status.get("alertas_recentes", [])
            ultima_verificacao = self.monitor_status.get(
                "ultima_verificacao", "N/A"
            )

            print(
                f"│ Sentinela Ativa: "
                f"{'SIM' if sentinela_ativa else 'NÃO':<37} │"
            )
            print(
                f"│ Conexão Ativa: "
                f"{'SIM' if conexao_ativa else 'NÃO':<38} │"
            )
            print(f"│ Total Alertas: {total_alertas:<41} │")
            print(f"│ Alertas Recentes: {len(alertas_recentes):<36} │")

            if alertas_recentes:
                ultimo_alerta = alertas_recentes[-1]
                print(
                    f"│ Último Alerta: "
                    f"{ultimo_alerta.get('timestamp', 'N/A'):<30} │"
                )
                print(f"│ Tipo: {ultimo_alerta.get('tipo', 'N/A'):<45} │")
            else:
                print(f"│ Último Alerta: {'N/A':<30} │")
                print(f"│ Tipo: {'N/A':<45} │")

            print(f"│ Última Verificação: {ultima_verificacao:<30} │")
        else:
            print("│ Aguardando dados do módulo MONITOR...                  │")

        print("└─────────────────────────────────────────────────────────────┘")
    
    def desenhar_painel_deep_packet(self) -> None:
        """Desenha o painel do módulo DEEP PACKET."""
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│                 MÓDULO DEEP PACKET                     │")
        print("├─────────────────────────────────────────────────────────────┤")

        if self.deep_packet_status:
            tunneis_detectados = self.deep_packet_status.get(
                "tunneis_detectados", []
            )
            ttl_analysis = self.deep_packet_status.get("ttl_analysis", {})
            ip_id_analysis = self.deep_packet_status.get("ip_id_analysis", {})

            print(f"│ Túneis Detectados: {len(tunneis_detectados):<35} │")

            if ttl_analysis:
                variance = ttl_analysis.get("variancia", 0)
                print(f"│ Variação TTL: {f'{variance:.2f}ms':<40} │")
            else:
                print(f"│ Variação TTL: {'N/A':<40} │")

            if ip_id_analysis:
                sequencial = ip_id_analysis.get("sequencial", False)
                print(
                    f"│ IP ID Sequencial: "
                    f"{'SIM' if sequencial else 'NÃO':<33} │"
                )
                print(
                    f"│ Double NAT: "
                    f"{'NÃO' if sequencial else 'SIM':<38} │"
                )
            else:
                print(f"│ IP ID Sequencial: {'N/A':<33} │")
                print(f"│ Double NAT: {'N/A':<38} │")

            if tunneis_detectados:
                print("│ ─────────────────────────────────────────────────── │")
                for tunel in tunneis_detectados[:3]:
                    dst = tunel.get("dst", "N/A")
                    porta = tunel.get("port", "N/A")
                    tipo = tunel.get("type", "N/A")
                    print(f"│ {f'{dst}:{porta} ({tipo})':<35} │")

        print("└─────────────────────────────────────────────────────────────┘")
    
    def desenhar_painel_logs(self) -> None:
        """Desenha o painel de logs recentes."""
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│                     LOGS RECENTES                        │")
        print("├─────────────────────────────────────────────────────────────┤")

        try:
            if os.path.exists("data/reports/pentest.log"):
                with open("data/reports/pentest.log", "r") as f:
                    lines = f.readlines()[-10:]

                    for line in lines:
                        if "ALERTA" in line:
                            print(f"│ 🔴 {line.strip()[:60]:<60} │")
                        elif "BANNER" in line and "404" in line:
                            print(f"│ 🟢 {line.strip()[:60]:<60} │")
                        elif "TUNNEL" in line:
                            print(f"│ 🟣 {line.strip()[:60]:<60} │")
                        elif "DOUBLE NAT" in line:
                            print(f"│ 🟠 {line.strip()[:60]:<60} │")
                        else:
                            print(f"│ ⚪ {line.strip()[:60]:<60} │")
            else:
                print("│ Nenhum log encontrado...                               │")
        except Exception:
            print("│ Erro ao ler logs...                                      │")

        print("└─────────────────────────────────────────────────────────────┘")
    
    def desenhar_menu_comandos(self) -> None:
        """Desenha o menu de comandos."""
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│                    COMANDOS RÁPIDOS                       │")
        print("├─────────────────────────────────────────────────────────────┤")
        print("│ [r] Scan Completo RECON    [m] Ver Alertas Monitor     │")
        print("│ [d] Análise Deep Packet    [l] Ver Logs Completos     │")
        print("│ [b] Ver Bandeiras         [s] Status do Sistema      │")
        print("│ [c] Limpar Tela           [q] Sair                    │")
        print("│ [h] Ajuda                                                      │")
        print("└─────────────────────────────────────────────────────────────┘")
    
    def mostrar_sugestao_deep_packet(self) -> None:
        """Mostra sugestão para ativar o Deep Packet."""
        if self.recon_status.get("servidor_detectado", False):
            print(
                "\n🎯 SUGESTÃO: Servidor detectado! "
                "Considere executar análise Deep Packet"
            )
            print("   Pressione [d] para iniciar análise profunda\n")
    
    def executar_dashboard(self) -> None:
        """Executa o dashboard principal."""
        print("Iniciando Dashboard Operação KALI...")
        print("Pressione Ctrl+C para encerrar")
        time.sleep(2)

        try:
            while self.running:
                self.limpar_tela()
                self.carregar_estados()

                self.desenhar_header()
                self.desenhar_painel_recon()
                self.desenhar_painel_monitor()
                self.desenhar_painel_deep_packet()
                self.desenhar_painel_bandeiras()
                self.desenhar_painel_logs()
                self.desenhar_menu_comandos()

                self.mostrar_sugestao_deep_packet()

                try:
                    comando = input("Comando: ").strip().lower()

                    if comando == "q":
                        self.running = False
                    elif comando == "c":
                        continue
                    elif comando == "h":
                        self.mostrar_ajuda()
                        input("Pressione Enter para continuar...")
                    elif comando == "l":
                        self.ver_logs_completos()
                        input("Pressione Enter para continuar...")
                    elif comando == "s":
                        self.mostrar_status_sistema()
                        input("Pressione Enter para continuar...")
                    else:
                        print("Comando inválido!")
                        time.sleep(1)

                except KeyboardInterrupt:
                    self.running = False
                except Exception:
                    continue

        except KeyboardInterrupt:
            self.running = False
            print("\nDashboard encerrado")
    
    def mostrar_ajuda(self) -> None:
        """Mostra a tela de ajuda."""
        self.limpar_tela()
        print("=" * 80)
        print("AJUDA - DASHBOARD KALI-CORE")
        print("=" * 80)
        print()
        print("COMANDOS:")
        print("  r - Executa scan completo do módulo RECON")
        print("  m - Mostra alertas recentes do módulo MONITOR")
        print("  d - Inicia análise Deep Packet (quando servidor detectado)")
        print("  l - Visualiza logs completos da operação")
        print("  s - Mostra status detalhado do sistema")
        print("  c - Limpa tela")
        print("  q - Sair do dashboard")
        print("  h - Mostra esta ajuda")
        print()
        print("MÓDULOS:")
        print("  RECON - Responsável por scan de portas e banner grabbing")
        print("  MONITOR - Monitoramento contínuo e alertas")
        print("  DEEP PACKET - Análise profunda de tráfego e Double NAT")
        print()
        print("ESTRUTURA:")
        print("  /core - Módulos do sistema")
        print("  /ui - Interfaces")
        print("  /data - Logs e relatórios")
        print("  /archive - Backup de versões antigas")
        print("=" * 80)
    
    def ver_logs_completos(self) -> None:
        """Visualiza os logs completos da operação."""
        self.limpar_tela()
        print("=" * 80)
        print("LOGS COMPLETOS DA OPERAÇÃO")
        print("=" * 80)
        print()

        try:
            if os.path.exists("data/reports/pentest.log"):
                with open("data/reports/pentest.log", "r") as f:
                    lines = f.readlines()

                    for line in lines[-50:]:
                        print(line.rstrip())
            else:
                print("Nenhum log encontrado.")
        except Exception as e:
            print(f"Erro ao ler logs: {e}")
    
    def mostrar_status_sistema(self) -> None:
        """Mostra o status detalhado do sistema."""
        self.limpar_tela()
        print("=" * 80)
        print("STATUS DETALHADO DO SISTEMA")
        print("=" * 80)
        print()

        print("MÓDULO RECON:")
        for key, value in self.recon_status.items():
            print(f"  {key}: {value}")
        print()

        print("MÓDULO MONITOR:")
        for key, value in self.monitor_status.items():
            print(f"  {key}: {value}")
        print()

        print("MÓDULO DEEP PACKET:")
        for key, value in self.deep_packet_status.items():
            print(f"  {key}: {value}")


def main() -> None:
    """Função principal do dashboard."""
    dashboard = DashboardKali()
    dashboard.executar_dashboard()


if __name__ == "__main__":
    main()
