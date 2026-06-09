import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

export const PaginaAuditoriaPublica: React.FC = () => {
  const { clienteSlug } = useParams<{ clienteSlug: string }>();
  const [clienteValido, setClienteValido] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [downloadIniciado, setDownloadIniciado] = useState(false);

  useEffect(() => {
    const validarCliente = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/assets/validate/${clienteSlug}`);
        const data = await response.json();
        setClienteValido(data.valid);
      } catch (error) {
        setClienteValido(false);
      } finally {
        setCarregando(false);
      }
    };

    if (clienteSlug) {
      validarCliente();
    }
  }, [clienteSlug]);

  const handleDownload = async () => {
    if (!clienteSlug) return;

    setDownloadIniciado(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/assets/download/powershell/${clienteSlug}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "asset_audit.ps1";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Erro ao baixar script:", error);
    }
  };

  if (carregando) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-600 font-sans">Carregando...</div>
      </div>
    );
  }

  if (!clienteValido) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded shadow-lg max-w-md">
          <h1 className="text-red-600 font-bold text-xl mb-4">Link Inválido</h1>
          <p className="text-gray-600">Este link de auditoria não é válido ou expirou.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header Corporativo */}
      <div className="bg-white border-b-4 border-blue-800 shadow-md">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-blue-800 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-bold">🛡️</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                Setor de Recursos Humanos & TI
              </h1>
              <p className="text-gray-600">Departamento de Segurança Cibernética</p>
            </div>
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="border-l-4 border-red-600 bg-red-50 p-4 mb-6">
            <h2 className="text-xl font-bold text-red-800 mb-2">
              COMUNICADO OFICIAL
            </h2>
            <p className="text-red-700 leading-relaxed">
              Este é um sistema automatizado de inventário e conformidade cibernética. 
              Em conformidade com as diretivas de segurança da instituição, todas as estações 
              de trabalho devem executar a ferramenta de verificação local nas próximas 24 horas.
            </p>
            <p className="text-red-700 leading-relaxed mt-2">
              As máquinas que não realizarem a validação até o término do prazo serão identificadas 
              como ativos não autorizados (Shadow IT) e terão suas credenciais e acessos suspensos 
              automaticamente no switch/roteador central da empresa.
            </p>
          </div>

          <div className="text-center py-8">
            <button
              onClick={handleDownload}
              disabled={downloadIniciado}
              className="bg-blue-800 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold text-lg py-4 px-8 rounded-lg shadow-lg transition-colors"
            >
              {downloadIniciado ? "Download Iniciado..." : "INICIAR VERIFICAÇÃO DE CONFORMIDADE DE HARDWARE"}
            </button>
          </div>

          <div className="border-t pt-6 mt-6">
            <h3 className="font-bold text-gray-800 mb-2">Instruções:</h3>
            <ol className="list-decimal list-inside text-gray-600 space-y-2">
              <li>Clique no botão acima para baixar o script de verificação</li>
              <li>Execute o script como Administrador (Windows) ou root (Linux)</li>
              <li>O script coletará informações de hardware e rede automaticamente</li>
              <li>Os dados serão enviados diretamente para o servidor de auditoria</li>
              <li>O script se autodestruirá após o envio bem-sucedido</li>
            </ol>
          </div>
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>Para suporte técnico, contate o departamento de TI</p>
          <p className="mt-1">© {new Date().getFullYear()} - Sistema de Auditoria Corporativa</p>
        </div>
      </div>
    </div>
  );
};
