import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:5190`;

interface Cliente {
  id: number;
  nome_cliente: string;
  ip: string;
  criado_em: string;
}

interface HistoricoClientesProps {
  refresh?: number;
}

export const HistoricoClientes: React.FC<HistoricoClientesProps> = ({ refresh }) => {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  const carregarClientes = async () => {
    setCarregando(true);
    setErro("");

    try {
      const response = await axios.get(`${API_URL}/api/clientes`);

      if (response.data.sucesso) {
        setClientes(response.data.clientes);
      } else {
        setErro("Erro ao carregar clientes");
      }
    } catch (error: any) {
      const mensagem = error.response?.data?.detail || error.message || "Erro ao carregar clientes";
      setErro(mensagem);
    } finally {
      setCarregando(false);
    }
  };

  // Carrega clientes apenas ao montar
  useEffect(() => {
    carregarClientes();
  }, []);

  // Recarrega quando refresh mudar (apenas se refresh > 0)
  useEffect(() => {
    if (refresh && refresh > 0) {
      carregarClientes();
    }
  }, [refresh]);

  const formatarData = (dataIso: string) => {
    if (!dataIso) return "-";
    try {
      const data = new Date(dataIso);
      return data.toLocaleString("pt-BR");
    } catch {
      return dataIso;
    }
  };

  const handleExcluir = async (clienteId: number, nomeCliente: string) => {
    if (!confirm(`Tem certeza que deseja excluir o cliente "${nomeCliente}"?`)) {
      return;
    }

    try {
      const response = await axios.delete(`${API_URL}/api/clientes/${clienteId}`);

      if (response.data.sucesso) {
        alert(`✓ ${response.data.mensagem}`);
        carregarClientes();
      }
    } catch (error: any) {
      const mensagem = error.response?.data?.detail || error.message || "Erro ao excluir cliente";
      alert(`✗ Erro: ${mensagem}`);
    }
  };

  return (
    <div className="historico-clientes border border-green-500 p-3 mb-3 bg-black">
      <div className="text-green-400 font-mono font-bold mb-3 text-sm flex justify-between items-center">
        <span>[ CLIENTES CADASTRADOS ]</span>
        <button
          onClick={carregarClientes}
          disabled={carregando}
          className="bg-green-900 hover:bg-green-700 disabled:opacity-50 text-green-400 font-mono text-xs py-1 px-2 border border-green-500 transition-colors"
        >
          {carregando ? "[ CARREGANDO... ]" : "[ ATUALIZAR ]"}
        </button>
      </div>

      {/* Mensagem de Erro */}
      {erro && (
        <div className="mb-2 p-2 border border-red-500 bg-red-900/20 text-red-400 font-mono text-xs rounded">
          ✗ {erro}
        </div>
      )}

      {/* Tabela de Clientes */}
      {clientes.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-xs text-green-400 border-collapse">
            <thead>
              <tr className="border-b border-green-500">
                <th className="text-left p-2 font-bold">[ ID ]</th>
                <th className="text-left p-2 font-bold">[ NOME DO CLIENTE ]</th>
                <th className="text-left p-2 font-bold">[ IP ]</th>
                <th className="text-left p-2 font-bold">[ CRIADO EM ]</th>
                <th className="text-center p-2 font-bold">[ AÇÕES ]</th>
              </tr>
            </thead>
            <tbody>
              {clientes.map((cliente) => (
                <tr
                  key={cliente.id}
                  className="border-b border-green-950 hover:bg-green-900/20 transition-colors"
                >
                  <td className="p-2">{cliente.id}</td>
                  <td className="p-2">{cliente.nome_cliente}</td>
                  <td className="p-2">{cliente.ip}</td>
                  <td className="p-2">{formatarData(cliente.criado_em)}</td>
                  <td className="p-2 text-center">
                    <button
                      onClick={() => handleExcluir(cliente.id, cliente.nome_cliente)}
                      className="bg-red-900 hover:bg-red-700 text-red-400 font-mono text-xs py-0.5 px-2 border border-red-500 transition-colors whitespace-nowrap"
                      title="Excluir cliente"
                    >
                      [ EXCLUIR ]
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-4 text-center border border-green-500 border-dashed">
          <div className="text-green-400 font-mono text-sm">
            [ Nenhum cliente cadastrado ]
          </div>
        </div>
      )}

      {/* Resumo */}
      <div className="mt-3 pt-2 border-t border-green-500 text-green-400 font-mono text-xs">
        <span>Total de clientes: {clientes.length}</span>
      </div>
    </div>
  );
};

export const HistoricoClientesMemo = React.memo(HistoricoClientes);
