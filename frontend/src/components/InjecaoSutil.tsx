import React, { useState, memo, useCallback, useEffect, useMemo, useRef } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

interface Cliente {
  id: number;
  nome_cliente: string;
  ip: string;
}

interface InjecaoSutilProps {
  onOperacaoIniciada: () => void;
  iniciarOperacao: (target: string, taticas: string[]) => Promise<any>;
  carregando: boolean;
}

interface ClientesState {
  clientes: Cliente[];
  carregando: boolean;
  inicializado: boolean;
}

export const InjecaoSutil: React.FC<InjecaoSutilProps> = ({ onOperacaoIniciada, iniciarOperacao, carregando }) => {

  // Estado do combobox de cliente (separado e isolado)
  const [clienteSelecionado, setClienteSelecionado] = useState("");

  // Estado da lista de clientes (lazy init)
  const [clientesState, setClientesState] = useState<ClientesState>({
    clientes: [],
    carregando: false,
    inicializado: false,
  });

  // Ref para garantir que a busca de clientes só execute uma vez
  const clientesCarregadosRef = useRef(false);

  // Estado das táticas
  const [taticas, setTaticas] = useState<string[]>([]);
  const [taticaCarregando, setTaticaCarregando] = useState<Record<string, boolean>>({});

  // Carrega clientes apenas uma vez ao montar
  useEffect(() => {
    if (clientesCarregadosRef.current) return;

    const buscarClientes = async () => {
      setClientesState((prev) => ({ ...prev, carregando: true }));
      try {
        const response = await axios.get(`${API_URL}/api/clientes`);
        if (response.data.sucesso) {
          setClientesState({
            clientes: response.data.clientes,
            carregando: false,
            inicializado: true,
          });
        }
      } catch (error) {
        console.error("Erro ao carregar clientes:", error);
        setClientesState((prev) => ({
          ...prev,
          carregando: false,
          inicializado: true,
        }));
      }
    };

    buscarClientes();
    clientesCarregadosRef.current = true;
  }, []);

  // Função para recarregar clientes manualmente
  const recarregarClientes = useCallback(async () => {
    setClientesState((prev) => ({ ...prev, carregando: true }));
    try {
      const response = await axios.get(`${API_URL}/api/clientes`);
      if (response.data.sucesso) {
        setClientesState({
          clientes: response.data.clientes,
          carregando: false,
          inicializado: true,
        });
      }
    } catch (error) {
      console.error("Erro ao carregar clientes:", error);
      setClientesState((prev) => ({
        ...prev,
        carregando: false,
      }));
    }
  }, []);

  const taticasDisponiveis = useMemo(
    () => [
      { id: "recon", label: "RECONHECIMENTO" },
      { id: "scan", label: "VARREDURA" },
      { id: "exploit", label: "EXPLORAÇÃO" },
      { id: "maint", label: "MANUTENÇÃO" },
      { id: "exfil", label: "EXFILTRAÇÃO" },
    ],
    []
  );

  const handleTaticaChange = useCallback(
    (taticaId: string, checked: boolean): void => {
      setTaticas((prev) =>
        checked ? [...prev, taticaId] : prev.filter((t) => t !== taticaId)
      );
    },
    []
  );

  const handleIniciar = useCallback(async (): Promise<void> => {
    if (!clienteSelecionado.trim()) {
      alert("Por favor, selecione um cliente");
      return;
    }
    if (taticas.length === 0) {
      alert("Por favor, selecione pelo menos uma tática");
      return;
    }

    const carregandoState: Record<string, boolean> = {};
    taticas.forEach((t) => {
      carregandoState[t] = true;
    });
    setTaticaCarregando(carregandoState);

    const resultado = await iniciarOperacao(clienteSelecionado, taticas);

    setTaticaCarregando({});

    if (resultado) {
      setClienteSelecionado("");
      setTaticas([]);
      onOperacaoIniciada();
    }
  }, [clienteSelecionado, taticas, iniciarOperacao, onOperacaoIniciada]);

  return (
    <div className="injecao-sutil border border-green-500 p-3 mb-3 bg-black">
      <div className="text-green-400 font-mono font-bold mb-2 text-sm">
        [ INJEÇÃO SUTIL ]
      </div>

      {/* Combobox de Cliente - Isolado */}
      <div className="mb-2 flex items-center gap-4">
        <label className="text-green-400 font-mono text-xs w-32 shrink-0">
          CLIENTE:
        </label>
        <select
          value={clienteSelecionado}
          onChange={(e) => setClienteSelecionado(e.target.value)}
          className="flex-1 bg-black border border-green-500 text-green-400 font-mono text-sm p-1.5 focus:outline-none focus:ring-1 focus:ring-green-500"
          disabled={carregando || clientesState.carregando}
        >
          <option value="">
            {clientesState.carregando
              ? "[ CARREGANDO... ]"
              : "[ SELECIONE UM CLIENTE ]"}
          </option>
          {clientesState.clientes.map((cliente) => (
            <option key={cliente.id} value={cliente.ip}>
              {cliente.nome_cliente} ({cliente.ip})
            </option>
          ))}
        </select>
        <button
          onClick={recarregarClientes}
          disabled={carregando || clientesState.carregando}
          className="bg-green-900 hover:bg-green-700 disabled:opacity-50 text-green-400 font-mono text-xs py-1.5 px-2 border border-green-500 transition-colors"
          title="Recarregar lista de clientes"
        >
          [ ↻ ]
        </button>
      </div>

      {/* Seleção de Táticas */}
      <div className="mb-2">
        <label className="text-green-400 font-mono text-xs block mb-1">
          TÁTICAS (Selecione ao menos uma):
        </label>
        <div className="grid grid-cols-2 gap-1">
          {taticasDisponiveis.map((tatica) => (
            <label
              key={tatica.id}
              className="flex items-center gap-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={taticas.includes(tatica.id)}
                onChange={(e) => handleTaticaChange(tatica.id, e.target.checked)}
                className="w-4 h-4 accent-green-500"
                disabled={carregando || taticaCarregando[tatica.id]}
              />
              <span className="text-green-400 font-mono text-xs">
                {taticaCarregando[tatica.id]
                  ? `${tatica.label}...`
                  : tatica.label}
              </span>
              {taticaCarregando[tatica.id] && (
                <span className="animate-spin text-green-400 text-xs">⟳</span>
              )}
            </label>
          ))}
        </div>
      </div>

      {/* Botão Iniciar */}
      <button
        onClick={handleIniciar}
        disabled={carregando}
        className="w-full bg-green-900 hover:bg-green-700 disabled:bg-gray-700 text-green-400 font-mono text-sm py-1.5 px-3 border border-green-500 transition-colors"
      >
        {carregando ? "[ PROCESSANDO... ]" : "[ INICIAR OPERAÇÃO ]"}
      </button>
    </div>
  );
};

export const InjecaoSutilMemo = memo(InjecaoSutil);
