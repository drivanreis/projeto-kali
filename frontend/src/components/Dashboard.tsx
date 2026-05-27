import React, { useState } from "react";
import { InjecaoSutil } from "./InjecaoSutil";
import { ModalAuditoria } from "./ModalAuditoria";
import { RelatorioCompliance } from "./RelatorioCompliance";
import { useApp } from "@/context/AppContext";

export const Dashboard: React.FC = () => {
  const { vulnerabilidades } = useApp();
  const [modalAberto, setModalAberto] = useState(false);
  const [relatorioAberto, setRelatorioAberto] = useState(false);
  const [vulnParaRelatorio, setVulnParaRelatorio] = useState<number[]>([]);

  const handleGerarLaudo = (vulnIds: number[]): void => {
    setVulnParaRelatorio(vulnIds);
    setRelatorioAberto(true);
    setModalAberto(false);
  };

  const vulnSelecionadas = vulnerabilidades.filter((v) => vulnParaRelatorio.includes(v.id));

  return (
    <div className="min-h-screen bg-black p-4 font-mono">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-green-400 text-2xl font-bold border-b border-green-500 pb-2">
          [ KALI-CORE V3.0 - FRAMEWORK DE AUDITORIA ]
        </h1>
      </div>

      {/* Container principal */}
      <div className="grid grid-cols-12 gap-4">
        {/* Coluna esquerda - Operações */}
        <div className="col-span-12 md:col-span-6">
          <InjecaoSutil
            onOperacaoIniciada={() => {
              setModalAberto(true);
            }}
          />

          {/* Painel de Status */}
          <div className="border border-green-500 p-4 mb-6 bg-black">
            <div className="text-green-400 font-bold mb-3 text-sm">[ STATUS DO SISTEMA ]</div>
            <div className="text-green-400 font-mono text-xs space-y-2">
              <div>
                Total de Vulnerabilidades:{" "}
                <span className="text-yellow-400">{vulnerabilidades.length}</span>
              </div>
              <div className="text-gray-500 text-xs mt-2">Sistema aguardando operações...</div>
            </div>
          </div>

          {/* Botões de Ação */}
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setModalAberto(true)}
              className="bg-green-900 hover:bg-green-700 text-green-400 font-mono text-xs py-2 px-3 border border-green-500 transition-colors"
            >
              [ AUDITORIA ]
            </button>
            <button
              onClick={() => {
                if (vulnerabilidades.length === 0) {
                  alert("Nenhuma vulnerabilidade para gerar relatório");
                  return;
                }
                setVulnParaRelatorio(vulnerabilidades.map((v) => v.id));
                setRelatorioAberto(true);
              }}
              className="bg-blue-900 hover:bg-blue-700 text-blue-400 font-mono text-xs py-2 px-3 border border-blue-500 transition-colors"
            >
              [ COMPLIANCE ]
            </button>
          </div>
        </div>

        {/* Coluna direita - Informações */}
        <div className="col-span-12 md:col-span-6">
          <div className="border border-green-500 p-4 bg-black">
            <div className="text-green-400 font-bold mb-3 text-sm">[ INFORMAÇÕES DO SISTEMA ]</div>
            <div className="text-gray-400 font-mono text-xs space-y-2">
              <div>
                <span className="text-green-400">Versão:</span> 3.0 (Vite + React + TypeScript)
              </div>
              <div>
                <span className="text-green-400">Backend:</span> FastAPI @ http://127.0.0.1:8001
              </div>
              <div>
                <span className="text-green-400">Frontend:</span> Vite @ http://localhost:5190
              </div>
              <div>
                <span className="text-green-400">Estado:</span> Conectado e pronto
              </div>
              <div className="mt-3 pt-3 border-t border-green-500">
                <p className="text-green-400 mb-1">Instruções:</p>
                <ul className="text-gray-400 text-xs space-y-1">
                  <li>1. Insira um IP/Domínio em "INJEÇÃO SUTIL"</li>
                  <li>2. Selecione táticas de teste</li>
                  <li>3. Clique em "INICIAR OPERAÇÃO"</li>
                  <li>4. Acesse "AUDITORIA" para visualizar vulnerabilidades</li>
                  <li>5. Selecione e gere "COMPLIANCE" para relatório executivo</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Auditoria */}
      <ModalAuditoria
        isOpen={modalAberto}
        onClose={() => setModalAberto(false)}
        onGerarLaudo={handleGerarLaudo}
      />

      {/* Relatório de Compliance */}
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
