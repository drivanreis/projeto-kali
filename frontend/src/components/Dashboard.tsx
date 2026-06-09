import React, { useState, useCallback } from "react";
import { InjecaoSutilMemo } from "./InjecaoSutil";
import { AuditoriaVulnerabilidades } from "./AuditoriaVulnerabilidades";
import { RelatorioCompliance } from "./RelatorioCompliance";
import { TerminalLogsMemo } from "./TerminalLogs";
import { FormularioCadastroClienteMemo } from "./FormularioCadastroCliente";
import { HistoricoClientesMemo } from "./HistoricoClientes";
import { InventarioAtivosMemo } from "./InventarioAtivos";
import { InvestigacaoForenseMemo } from "./InvestigacaoForense";
import { useApp } from "@/context/AppContext";

export const Dashboard: React.FC = () => {
  const { vulnerabilidades, logs, iniciarOperacao, carregando } = useApp();
  const [relatorioAberto, setRelatorioAberto] = useState(false);
  const [vulnParaRelatorio, setVulnParaRelatorio] = useState<number[]>([]);
  const [abaAtiva, setAbaAtiva] = useState<1 | 2 | 3 | 4 | 5>(1);
  const [clienteCriadoRefresh, setClienteCriadoRefresh] = useState(0);

  const handleGerarLaudo = useCallback((vulnIds: number[]): void => {
    setVulnParaRelatorio(vulnIds);
    setRelatorioAberto(true);
  }, []);

  const handleOperacaoIniciada = useCallback(() => {
    // Ao iniciar operação, podemos dar feedback visual mantendo na aba 2
  }, []);

  const vulnSelecionadas = vulnerabilidades.filter((v) => vulnParaRelatorio.includes(v.id));

  return (
    <div className="min-h-screen bg-black p-3 font-mono">
      {/* Header e Menu de Navegação Global */}
      <div className="mb-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-green-500 pb-3 gap-3">
          <h1 className="text-green-400 text-2xl font-bold font-mono">
            [ KALI-CORE V3.0 ]
          </h1>
          <nav className="flex flex-wrap gap-2">
            <button
              onClick={() => setAbaAtiva(1)}
              className={`font-mono text-xs md:text-sm py-1.5 px-3 border transition-colors ${
                abaAtiva === 1
                  ? "bg-green-900 border-green-500 text-green-400 font-bold"
                  : "bg-black border-green-900 text-green-700 hover:text-green-500 hover:border-green-500"
              }`}
            >
              [ 1 - cadastro de clientes ]
            </button>
            <button
              onClick={() => setAbaAtiva(2)}
              className={`font-mono text-xs md:text-sm py-1.5 px-3 border transition-colors ${
                abaAtiva === 2
                  ? "bg-green-900 border-green-500 text-green-400 font-bold"
                  : "bg-black border-green-900 text-green-700 hover:text-green-500 hover:border-green-500"
              }`}
            >
              [ 2 - ações / serviços ]
            </button>
            <button
              onClick={() => setAbaAtiva(3)}
              className={`font-mono text-xs md:text-sm py-1.5 px-3 border transition-colors ${
                abaAtiva === 3
                  ? "bg-green-900 border-green-500 text-green-400 font-bold"
                  : "bg-black border-green-900 text-green-700 hover:text-green-500 hover:border-green-500"
              }`}
            >
              [ 3 - auditoria / compliance ]
            </button>
            <button
              onClick={() => setAbaAtiva(4)}
              className={`font-mono text-xs md:text-sm py-1.5 px-3 border transition-colors ${
                abaAtiva === 4
                  ? "bg-green-900 border-green-500 text-green-400 font-bold"
                  : "bg-black border-green-900 text-green-700 hover:text-green-500 hover:border-green-500"
              }`}
            >
              [ 4 - inventário e ativos ]
            </button>
            <button
              onClick={() => setAbaAtiva(5)}
              className={`font-mono text-xs md:text-sm py-1.5 px-3 border transition-colors ${
                abaAtiva === 5
                  ? "bg-green-900 border-green-500 text-green-400 font-bold"
                  : "bg-black border-green-900 text-green-700 hover:text-green-500 hover:border-green-500"
              }`}
            >
              [ 5 - investigação forense ]
            </button>
          </nav>
        </div>
      </div>

      {/* Container principal com Renderização Condicional */}
      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-12">
          {abaAtiva === 1 && (
            <>
              {/* Cadastro de Cliente */}
              <FormularioCadastroClienteMemo
                onClienteCriado={() => setClienteCriadoRefresh((prev) => prev + 1)}
                refresh={clienteCriadoRefresh}
              />

              {/* Histórico de Clientes */}
              <HistoricoClientesMemo refresh={clienteCriadoRefresh} />
              
              {/* Histórico de Logs e Operações */}
              <div className="border border-green-500 p-4 bg-black">
                <div className="text-green-400 font-mono font-bold mb-3 text-sm">
                  [ HISTÓRICO DE LOGS E OPERAÇÕES ]
                </div>
                {logs.length === 0 ? (
                  <div className="text-gray-500 text-xs font-mono">Nenhum registro histórico disponível.</div>
                ) : (
                  <div className="bg-black border border-green-900 p-3 h-[250px] overflow-y-auto font-mono text-xs space-y-1">
                    {logs.map((log, index) => (
                      <div key={index} className="mb-1">
                        <span className="text-gray-500">[{log.timestamp}]</span>{" "}
                        <span
                          className={
                            log.level === "INFO"
                              ? "text-green-400"
                              : log.level === "WARNING"
                              ? "text-yellow-400"
                              : log.level === "ERROR"
                              ? "text-red-400"
                              : "text-blue-400"
                          }
                        >
                          [{log.level}]
                        </span>{" "}
                        <span className="text-green-300">{log.message}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          {abaAtiva === 2 && (
            <>
              {/* Injeção Sutil */}
              <InjecaoSutilMemo
                onOperacaoIniciada={handleOperacaoIniciada}
                iniciarOperacao={iniciarOperacao}
                carregando={carregando}
              />

              {/* Terminal de Logs */}
              <TerminalLogsMemo logs={logs} title="[ TERMINAL DE LOGS ]" />

              {/* Status do Sistema */}
              <div className="border border-green-500 p-3 mb-3 bg-black">
                <div className="text-green-400 font-bold mb-2 text-sm">
                  [ STATUS DO SISTEMA ]
                </div>
                <div className="text-green-400 font-mono text-xs space-y-1">
                  <div>
                    Total de Vulnerabilidades:{" "}
                    <span className="text-yellow-400">{vulnerabilidades.length}</span>
                  </div>
                  <div className="text-gray-500 text-xs mt-1">
                    {carregando ? "Operação em execução..." : "Sistema aguardando operações..."}
                  </div>
                </div>
              </div>
            </>
          )}

          {abaAtiva === 3 && (
            <AuditoriaVulnerabilidades
              onGerarLaudo={handleGerarLaudo}
              onFechar={() => setAbaAtiva(1)}
            />
          )}

          {abaAtiva === 4 && (
            <InventarioAtivosMemo refresh={clienteCriadoRefresh} />
          )}

          {abaAtiva === 5 && (
            <InvestigacaoForenseMemo />
          )}
        </div>
      </div>

      {/* Relatório de Compliance (Overlay de Impressão) */}
      {relatorioAberto && (
        <RelatorioCompliance
          vulnerabilidades={vulnSelecionadas}
          onFechar={() => {
            setRelatorioAberto(false);
            setVulnParaRelatorio([]);
          }}
        />
      )}
    </div>
  );
};
