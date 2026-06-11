import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:5190`;

interface Cliente {
  id: number;
  nome_cliente: string;
  ip: string;
  criado_em: string;
}

interface FormularioCadastroClienteProps {
  onClienteCriado?: () => void;
  refresh?: number;
}

export const FormularioCadastroCliente: React.FC<FormularioCadastroClienteProps> = ({
  onClienteCriado,
  refresh,
}) => {
  const [nomeCliente, setNomeCliente] = useState("");
  const [ip, setIp] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [mensagemSucesso, setMensagemSucesso] = useState("");
  const [mensagemErro, setMensagemErro] = useState("");
  
  // Lista de clientes e estado de navegação
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const nomeRef = useRef<HTMLInputElement>(null);
  const ipRef = useRef<HTMLInputElement>(null);
  const [isNomeFocused, setIsNomeFocused] = useState(false);
  const [isIpFocused, setIsIpFocused] = useState(false);

  // Busca lista de clientes para navegação
  const carregarClientes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/clientes`);
      if (response.data.sucesso) {
        const list = response.data.clientes || [];
        setClientes(list);
        
        // Se temos um cliente selecionado, atualiza o index na nova lista
        if (selectedId !== null) {
          const idx = list.findIndex((c: Cliente) => c.id === selectedId);
          if (idx !== -1) {
            setCurrentIndex(idx);
          } else {
            handleNovo();
          }
        }
      }
    } catch (error) {
      console.error("Erro ao carregar lista de clientes:", error);
    }
  };

  // Mantém a lista atualizada
  useEffect(() => {
    void carregarClientes();
  }, [refresh]);

  // Mantém o foco nos inputs durante re-renderizações
  useEffect(() => {
    if (isNomeFocused && nomeRef.current) {
      nomeRef.current.focus();
    }
  });

  useEffect(() => {
    if (isIpFocused && ipRef.current) {
      ipRef.current.focus();
    }
  });

  const handleNomeFocus = () => setIsNomeFocused(true);
  const handleNomeBlur = () => setIsNomeFocused(false);
  const handleIpFocus = () => setIsIpFocused(true);
  const handleIpBlur = () => setIsIpFocused(false);

  // Navegação
  const carregarClienteAtIndex = (idx: number) => {
    const c = clientes[idx];
    if (c) {
      setCurrentIndex(idx);
      setSelectedId(c.id);
      setNomeCliente(c.nome_cliente);
      setIp(c.ip);
      setMensagemSucesso("");
      setMensagemErro("");
    }
  };

  const handlePrimeiro = () => {
    if (clientes.length === 0) return;
    carregarClienteAtIndex(0);
  };

  const handleAnterior = () => {
    if (clientes.length === 0) return;
    if (currentIndex === null) {
      carregarClienteAtIndex(clientes.length - 1);
    } else if (currentIndex > 0) {
      carregarClienteAtIndex(currentIndex - 1);
    }
  };

  const handleProximo = () => {
    if (clientes.length === 0) return;
    if (currentIndex === null) {
      carregarClienteAtIndex(0);
    } else if (currentIndex < clientes.length - 1) {
      carregarClienteAtIndex(currentIndex + 1);
    }
  };

  const handleUltimo = () => {
    if (clientes.length === 0) return;
    carregarClienteAtIndex(clientes.length - 1);
  };

  const handleNovo = () => {
    setNomeCliente("");
    setIp("");
    setCurrentIndex(null);
    setSelectedId(null);
    setMensagemSucesso("");
    setMensagemErro("");
    if (nomeRef.current) {
      nomeRef.current.focus();
    }
  };

  const handleSalvar = async () => {
    setMensagemSucesso("");
    setMensagemErro("");

    // Validações
    if (!nomeCliente.trim()) {
      setMensagemErro("Nome do cliente é obrigatório");
      return;
    }

    if (!ip.trim()) {
      setMensagemErro("IP do cliente é obrigatório");
      return;
    }

    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipRegex.test(ip.trim())) {
      setMensagemErro("IP inválido. Use o formato XXX.XXX.XXX.XXX");
      return;
    }

    setCarregando(true);

    try {
      const payload = {
        nome_cliente: nomeCliente.trim(),
        ip: ip.trim(),
      };

      if (selectedId !== null) {
        // Editar existente - PUT
        const response = await axios.put(`${API_URL}/api/clientes/${selectedId}`, payload);
        if (response.status === 200) {
          setMensagemSucesso("Cliente atualizado com sucesso!");
          await carregarClientes();
          if (onClienteCriado) {
            onClienteCriado();
          }
        }
      } else {
        // Criar novo - POST
        const response = await axios.post(`${API_URL}/api/clientes`, payload);
        if (response.status === 200) {
          setMensagemSucesso(`Cliente criado com sucesso (ID: ${response.data.id})`);
          const novoId = response.data.id;
          if (onClienteCriado) {
            onClienteCriado();
          }
          
          // Recarrega e foca no novo
          const freshRes = await axios.get(`${API_URL}/api/clientes`);
          if (freshRes.data.sucesso) {
            const list = freshRes.data.clientes || [];
            setClientes(list);
            const idx = list.findIndex((c: Cliente) => c.id === novoId);
            if (idx !== -1) {
              setCurrentIndex(idx);
              setSelectedId(novoId);
              setNomeCliente(list[idx].nome_cliente);
              setIp(list[idx].ip);
            }
          }
        }
      }
    } catch (error: any) {
      const mensagem = error.response?.data?.detail || error.message || "Erro ao salvar cliente";
      setMensagemErro(`Erro: ${mensagem}`);
    } finally {
      setCarregando(false);
    }
  };

  const handlePesquisar = () => {
    const termo = prompt("Digite o nome ou IP do cliente para pesquisar:");
    if (termo === null) return;
    
    if (!termo.trim()) {
      alert("Por favor, digite um termo de pesquisa.");
      return;
    }

    const termoBusca = termo.trim().toLowerCase();
    const found = clientes.find(
      (c) =>
        c.nome_cliente.toLowerCase().includes(termoBusca) ||
        c.ip.includes(termoBusca)
    );

    if (found) {
      const idx = clientes.indexOf(found);
      carregarClienteAtIndex(idx);
    } else {
      alert("Nenhum cliente correspondente encontrado.");
    }
  };

  const handleExcluirAtual = async () => {
    if (selectedId === null) return;
    
    if (!confirm(`Tem certeza que deseja excluir o cliente "${nomeCliente}"?`)) {
      return;
    }

    setCarregando(true);
    try {
      const response = await axios.delete(`${API_URL}/api/clientes/${selectedId}`);
      if (response.data.sucesso) {
        setMensagemSucesso("Cliente excluído com sucesso.");
        handleNovo();
        if (onClienteCriado) {
          onClienteCriado();
        }
      }
    } catch (error: any) {
      const mensagem = error.response?.data?.detail || error.message || "Erro ao excluir cliente";
      setMensagemErro(`Erro: ${mensagem}`);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="formulario-cadastro-cliente border border-green-500 p-3 mb-3 bg-black">
      <div className="text-green-400 font-mono font-bold mb-3 text-sm flex justify-between items-center">
        <span>[ NOVO CLIENTE ]</span>
        {selectedId && (
          <span className="text-green-500 text-[10px]">
            [ REGISTRO: {currentIndex !== null ? currentIndex + 1 : "?"} / {clientes.length} ]
          </span>
        )}
      </div>

      {/* Campos Nome e IP - Alinhamento Horizontal */}
      <div className="mb-3 flex flex-row items-center gap-4">
        <div className="flex items-center gap-4 flex-1">
          <label className="text-green-400 font-mono text-xs w-32 shrink-0">
            NOME DO CLIENTE:
          </label>
          <input
            ref={nomeRef}
            type="text"
            value={nomeCliente}
            onChange={(e) => setNomeCliente(e.target.value)}
            onFocus={handleNomeFocus}
            onBlur={handleNomeBlur}
            placeholder="Digite o nome do cliente"
            className="flex-1 bg-black border border-green-500 text-green-400 font-mono text-sm p-1.5 focus:outline-none focus:ring-1 focus:ring-green-500 disabled:opacity-50"
            disabled={carregando}
          />
        </div>
        <div className="flex items-center gap-4 flex-1">
          <label className="text-green-400 font-mono text-xs w-32 shrink-0">
            IP DO CLIENTE:
          </label>
          <input
            ref={ipRef}
            type="text"
            value={ip}
            onChange={(e) => setIp(e.target.value)}
            onFocus={handleIpFocus}
            onBlur={handleIpBlur}
            placeholder="192.168.1.1"
            className="flex-1 bg-black border border-green-500 text-green-400 font-mono text-sm p-1.5 focus:outline-none focus:ring-1 focus:ring-green-500 disabled:opacity-50"
            disabled={carregando}
          />
        </div>
      </div>

      {/* Mensagens de Feedback */}
      {mensagemSucesso && (
        <div className="mb-2 p-2 border border-green-500 bg-green-900/20 text-green-400 font-mono text-xs rounded-none">
          ✓ {mensagemSucesso}
        </div>
      )}

      {mensagemErro && (
        <div className="mb-2 p-2 border border-red-500 bg-red-900/20 text-red-400 font-mono text-xs rounded-none">
          ✗ {mensagemErro}
        </div>
      )}

      {/* Toolbar de Navegação e Edição (Fita Horizontal) */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handlePrimeiro}
          disabled={carregando || clientes.length === 0}
          className="bg-black hover:bg-green-900 border border-green-500 disabled:opacity-30 disabled:hover:bg-black text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Primeiro cliente"
        >
          [ &lt; ]
        </button>
        <button
          onClick={handleAnterior}
          disabled={carregando || clientes.length === 0 || currentIndex === 0}
          className="bg-black hover:bg-green-900 border border-green-500 disabled:opacity-30 disabled:hover:bg-black text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Cliente anterior"
        >
          [ &lt;&lt; ]
        </button>
        <button
          onClick={handleProximo}
          disabled={carregando || clientes.length === 0 || currentIndex === clientes.length - 1}
          className="bg-black hover:bg-green-900 border border-green-500 disabled:opacity-30 disabled:hover:bg-black text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Próximo cliente"
        >
          [ &gt;&gt; ]
        </button>
        <button
          onClick={handleUltimo}
          disabled={carregando || clientes.length === 0}
          className="bg-black hover:bg-green-900 border border-green-500 disabled:opacity-30 disabled:hover:bg-black text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Último cliente"
        >
          [ &gt; ]
        </button>
        <button
          onClick={handleNovo}
          disabled={carregando}
          className="bg-black hover:bg-green-900 border border-green-500 text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Novo cliente"
        >
          [ + ]
        </button>
        <button
          onClick={handleSalvar}
          disabled={carregando}
          className="bg-green-950 hover:bg-green-900 border border-green-500 text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Gravar registro"
        >
          [ 💾 ]
        </button>
        <button
          onClick={handlePesquisar}
          disabled={carregando || clientes.length === 0}
          className="bg-black hover:bg-green-900 border border-green-500 disabled:opacity-30 disabled:hover:bg-black text-green-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Pesquisar por nome ou IP"
        >
          [ P ]
        </button>
        <button
          onClick={handleExcluirAtual}
          disabled={carregando || selectedId === null}
          className="bg-red-950 hover:bg-red-900 border border-red-500 disabled:opacity-30 disabled:hover:bg-black text-red-400 font-mono text-xs py-1 px-3 transition-colors"
          title="Excluir cliente atual"
        >
          [ ❌ ]
        </button>
      </div>
    </div>
  );
};

export const FormularioCadastroClienteMemo = React.memo(FormularioCadastroCliente);
