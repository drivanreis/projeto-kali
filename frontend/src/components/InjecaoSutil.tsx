import React, { useState } from "react";
import { useApp } from "@/context/AppContext";

interface InjecaoSutilProps {
  onOperacaoIniciada: () => void;
}

export const InjecaoSutil: React.FC<InjecaoSutilProps> = ({ onOperacaoIniciada }) => {
  const { iniciarOperacao, carregando } = useApp();
  const [alvo, setAlvo] = useState("");
  const [taticas, setTaticas] = useState<string[]>([]);

  const taticasDisponiveis = [
    { id: "recon", label: "RECONHECIMENTO" },
    { id: "scan", label: "VARREDURA" },
    { id: "exploit", label: "EXPLORAÇÃO" },
    { id: "maint", label: "MANUTENÇÃO" },
    { id: "exfil", label: "EXFILTRAÇÃO" },
  ];

  const handleTaticaChange = (taticaId: string, checked: boolean): void => {
    setTaticas((prev) => (checked ? [...prev, taticaId] : prev.filter((t) => t !== taticaId)));
  };

  const handleIniciar = async (): Promise<void> => {
    if (!alvo.trim()) {
      alert("Por favor, informe um alvo (IP ou domínio)");
      return;
    }
    if (taticas.length === 0) {
      alert("Por favor, selecione pelo menos uma tática");
      return;
    }

    const resultado = await iniciarOperacao(alvo, taticas);
    if (resultado) {
      setAlvo("");
      setTaticas([]);
      onOperacaoIniciada();
    }
  };

  return (
    <div className="injecao-sutil border border-green-500 p-4 mb-6 bg-black">
      <div className="text-green-400 font-mono font-bold mb-3 text-sm">[ INJEÇÃO SUTIL ]</div>

      <div className="mb-4">
        <label className="text-green-400 font-mono text-xs block mb-2">ALVO (IP / DOMÍNIO):</label>
        <input
          type="text"
          value={alvo}
          onChange={(e) => setAlvo(e.target.value)}
          placeholder="192.168.1.1 ou exemplo.com"
          className="w-full bg-black border border-green-500 text-green-400 font-mono text-sm p-2 focus:outline-none focus:ring-1 focus:ring-green-500"
          disabled={carregando}
        />
      </div>

      <div className="mb-4">
        <label className="text-green-400 font-mono text-xs block mb-2">
          TÁTICAS (Selecione ao menos uma):
        </label>
        <div className="grid grid-cols-2 gap-2">
          {taticasDisponiveis.map((tatica) => (
            <label key={tatica.id} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={taticas.includes(tatica.id)}
                onChange={(e) => handleTaticaChange(tatica.id, e.target.checked)}
                className="w-4 h-4 accent-green-500"
                disabled={carregando}
              />
              <span className="text-green-400 font-mono text-xs">{tatica.label}</span>
            </label>
          ))}
        </div>
      </div>

      <button
        onClick={handleIniciar}
        disabled={carregando}
        className="w-full bg-green-900 hover:bg-green-700 disabled:bg-gray-700 text-green-400 font-mono text-sm py-2 px-3 border border-green-500 transition-colors"
      >
        {carregando ? "[ PROCESSANDO... ]" : "[ INICIAR OPERAÇÃO ]"}
      </button>
    </div>
  );
};
