import React, { useState, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

interface InventarioAtivosProps {
  refresh?: number;
}

export const InventarioAtivos: React.FC<InventarioAtivosProps> = ({ refresh }) => {
  const [auditLink, setAuditLink] = useState("");
  const [copied, setCopied] = useState(false);
  const [ativosRecebidos, setAtivosRecebidos] = useState<any[]>([]);

  // Captura IP local do servidor e gera URL do coletor porta 8888
  useEffect(() => {
    const gerarLinkColetor = () => {
      // Captura IP local do servidor (hostname ou window.location)
      const hostname = window.location.hostname;
      const port = "8888";
      const link = `http://${hostname}:${port}/audit`;
      setAuditLink(link);
    };

    gerarLinkColetor();
  }, []);

  // Busca ativos recebidos periodicamente
  useEffect(() => {
    const carregarAtivos = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/assets/all`);
        const data = await response.json();
        if (data.success) {
          setAtivosRecebidos(data.ativos);
        }
      } catch (error) {
        console.error("Erro ao carregar ativos:", error);
      }
    };

    carregarAtivos();
    const interval = setInterval(carregarAtivos, 5000); // Atualiza a cada 5 segundos

    return () => clearInterval(interval);
  }, [refresh]);

  const handleCopyLink = () => {
    navigator.clipboard.writeText(auditLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="inventario-ativos border border-green-500 p-3 mb-3 bg-black">
      <div className="text-green-400 font-mono font-bold mb-3 text-sm">
        [ 4 - INVENTÁRIO E ATIVOS (BLUE TEAM) ]
      </div>

      {/* Configuração de Auditoria de Conformidade (RH) */}
      <div className="mb-3 border border-green-900 p-3 bg-black">
        <div className="text-green-400 font-mono font-bold mb-2 text-sm">
          [ CONFIGURAÇÃO DE AUDITORIA DE CONFORMIDADE (RH) ]
        </div>

        {/* Link Dinâmico do Coletor */}
        <div className="mb-3 flex items-center gap-2">
          <label className="text-green-400 font-mono text-xs w-32 shrink-0">
            LINK AUDITORIA:
          </label>
          <input
            type="text"
            value={auditLink}
            readOnly
            className="flex-1 bg-black border border-green-500 text-green-400 font-mono text-sm p-1.5 focus:outline-none"
          />
          <button
            onClick={handleCopyLink}
            className="bg-green-900 hover:bg-green-700 text-green-400 font-mono text-xs py-1.5 px-3 border border-green-500 transition-colors"
          >
            {copied ? "[ COPIADO! ]" : "[ COPIAR LINK ]"}
          </button>
        </div>
      </div>

      {/* Preview em Iframe */}
      <div className="mb-3 border border-green-900 p-3 bg-black">
        <div className="text-green-400 font-mono font-bold mb-2 text-sm">
          [ VISUALIZAÇÃO DA PÁGINA DO FUNCIONÁRIO (IFRAME) ]
        </div>
        <div className="border border-green-900 bg-black">
          <iframe
            src="http://localhost:8888/audit"
            className="w-full h-[400px] border-0"
            title="Preview da página de auditoria"
            sandbox="allow-same-origin allow-scripts"
          />
        </div>
      </div>

      {/* Tabela de Ativos Recebidos */}
      <div className="border border-green-900 p-3 bg-black">
        <div className="text-green-400 font-mono font-bold mb-2 text-sm">
          [ ATIVOS RECEBIDOS EM TEMPO REAL ]
        </div>
        {ativosRecebidos.length === 0 ? (
          <div className="text-gray-500 text-xs font-mono">Nenhum ativo recebido ainda.</div>
        ) : (
          <div className="space-y-2">
            {ativosRecebidos.map((ativo, index) => (
              <div
                key={index}
                className={`border p-2 ${
                  ativo.alerta ? "border-red-500 bg-red-900/10" : "border-green-900"
                }`}
              >
                <div className="text-green-400 font-mono text-xs font-bold mb-1">
                  {ativo.computer_name} - {ativo.username}
                </div>
                <div className="text-green-400 font-mono text-xs space-y-1">
                  <div>IP Interno: {ativo.ip_address}</div>
                  <div>MAC Address: {ativo.mac_address}</div>
                  <div>Vizinhos na Rede: {ativo.neighbors?.join(", ") || "Nenhum"}</div>
                  {ativo.alerta && (
                    <div className="text-red-400 font-mono text-xs mt-1">
                      ⚠️ ALERTA: Detectados dispositivos não homologados na rede
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export const InventarioAtivosMemo = React.memo(InventarioAtivos);
