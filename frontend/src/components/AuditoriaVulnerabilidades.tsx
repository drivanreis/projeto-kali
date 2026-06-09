import React, { useState, useMemo, useEffect } from "react";
import { useApp } from "@/context/AppContext";
import { CardVulnerabilidade } from "./CardVulnerabilidade";
import { ComboBoxCliente } from "./ComboBoxCliente";

interface AuditoriaVulnerabilidadesProps {
  onGerarLaudo: (vulnIds: number[]) => void;
  onFechar: () => void;
}

export const AuditoriaVulnerabilidades: React.FC<AuditoriaVulnerabilidadesProps> = ({
  onGerarLaudo,
  onFechar,
}) => {
  const {
    vulnerabilidades,
    clientesIps,
    attackTypes,
    filtroCliente,
    filtroAtaque,
    setFiltroCliente,
    setFiltroAtaque,
    carregarFiltros,
  } = useApp();

  const [selecionadas, setSelecionadas] = useState<Set<number>>(new Set());

  // Garante que os filtros sejam carregados ao montar a página
  useEffect(() => {
    void carregarFiltros();
  }, [carregarFiltros]);

  // Filtra as vulnerabilidades baseadas no cliente e tipo de ataque
  const vulnerabilidadesFiltradas = useMemo(() => {
    return vulnerabilidades.filter((v) => {
      const matchCliente = !filtroCliente || v.alvo_ip === filtroCliente;
      const matchAtaque = !filtroAtaque || v.attack_type === filtroAtaque;
      return matchCliente && matchAtaque;
    });
  }, [vulnerabilidades, filtroCliente, filtroAtaque]);

  const handleSelectVuln = (id: number): void => {
    setSelecionadas((prev) => {
      const novo = new Set(prev);
      if (novo.has(id)) {
        novo.delete(id);
      } else {
        novo.add(id);
      }
      return novo;
    });
  };

  const handleGerarLaudo = (): void => {
    if (selecionadas.size === 0) {
      alert("Por favor, selecione pelo menos uma vulnerabilidade");
      return;
    }
    onGerarLaudo(Array.from(selecionadas));
  };

  return (
    <div className="border-2 border-green-500 bg-black w-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-green-500 p-4 bg-black flex-shrink-0 flex justify-between items-center">
        <div className="text-green-400 font-mono font-bold text-sm">
          [ AUDITORIA DE VULNERABILIDADES ]
        </div>
        <button
          onClick={onFechar}
          className="text-green-400 hover:text-red-400 font-mono font-bold text-sm"
          title="Fechar e Voltar"
        >
          ✕
        </button>
      </div>

      {/* Filtros e Stats */}
      <div className="p-4 border-b border-green-950">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
          <ComboBoxCliente
            clientes={clientesIps}
            valor={filtroCliente}
            onChange={setFiltroCliente}
            label="IP / DOMÍNIO:"
          />
          <div>
            <label className="text-green-400 font-mono text-xs block mb-1">TIPO DE ATAQUE:</label>
            <select
              id="filtro-ataque"
              value={filtroAtaque}
              onChange={(e) => setFiltroAtaque(e.target.value)}
              className="w-full bg-black border border-green-500 text-green-400 font-mono text-xs p-2 focus:outline-none"
            >
              <option value="">-- TODOS --</option>
              {attackTypes.map((tipo) => (
                <option key={tipo} value={tipo}>
                  {tipo}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="text-gray-400 font-mono text-xs">
          Total: {vulnerabilidadesFiltradas.length} | Selecionadas: {selecionadas.size}
        </div>
      </div>

      {/* Lista de cards (scrollable) */}
      <div className="overflow-y-auto p-4 max-h-[400px] min-h-[250px] bg-black">
        {vulnerabilidadesFiltradas.length === 0 ? (
          <div className="text-gray-500 text-center font-mono text-xs py-8 border border-dashed border-green-950">
            Nenhuma vulnerabilidade encontrada com os filtros selecionados
          </div>
        ) : (
          vulnerabilidadesFiltradas.map((vuln) => (
            <CardVulnerabilidade
              key={vuln.id}
              vulnerabilidade={vuln}
              selecionada={selecionadas.has(vuln.id)}
              onSelect={handleSelectVuln}
            />
          ))
        )}
      </div>

      {/* Botões do rodapé */}
      <div className="border-t border-green-500 p-4 bg-black flex flex-row gap-4">
        <button
          onClick={handleGerarLaudo}
          className="flex-1 bg-green-900 hover:bg-green-700 text-green-400 font-mono text-xs py-2 px-3 border border-green-500 transition-colors"
        >
          [ GERAR LAUDO ]
        </button>
        <button
          onClick={onFechar}
          className="flex-1 bg-red-900 hover:bg-red-700 text-red-400 font-mono text-xs py-2 px-3 border border-red-500 transition-colors"
        >
          [ FECHAR ]
        </button>
      </div>
    </div>
  );
};
