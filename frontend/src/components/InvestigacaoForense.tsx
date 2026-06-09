import React, { useState, useEffect } from "react";

const FORENSE_AGENT_PORT = 8888;
const FORENSE_AGENT_URL = `http://localhost:${FORENSE_AGENT_PORT}`;

interface DiskInfo {
  number: number;
  path: string;
  size?: number;
  type?: string;
}

interface ScanProgress {
  status: "idle" | "scanning" | "completed" | "error";
  progress: number;
  current_block?: number;
  total_blocks?: number;
  files_found?: number;
}

interface RecoveredFile {
  name: string;
  size: number;
  offset: number;
  type?: string;
}

export const InvestigacaoForense: React.FC = () => {
  const [agentConnected, setAgentConnected] = useState(false);
  const [disks, setDisks] = useState<DiskInfo[]>([]);
  const [selectedDisk, setSelectedDisk] = useState<number | null>(null);
  const [scanProgress, setScanProgress] = useState<ScanProgress>({
    status: "idle",
    progress: 0,
  });
  const [recoveredFiles, setRecoveredFiles] = useState<RecoveredFile[]>([]);
  const [error, setError] = useState<string>("");
  const [logs, setLogs] = useState<string[]>([]);

  // Verifica se o agente está rodando
  useEffect(() => {
    const checkAgent = async () => {
      try {
        const response = await fetch(`${FORENSE_AGENT_URL}/status`);
        if (response.ok) {
          setAgentConnected(true);
          addLog("Agente forense conectado com sucesso");
        } else {
          setAgentConnected(false);
          addLog("Agente forense não encontrado");
        }
      } catch {
        setAgentConnected(false);
        addLog("Agente forense não encontrado - inicie o agente local");
      }
    };

    checkAgent();
    const interval = setInterval(checkAgent, 5000);
    return () => clearInterval(interval);
  }, []);

  // Carrega lista de discos disponíveis
  const loadDisks = async () => {
    try {
      const response = await fetch(`${FORENSE_AGENT_URL}/disks`);
      const data = await response.json();
      if (data.success) {
        setDisks(data.disks);
        addLog(`Discos disponíveis: ${data.disks.length}`);
      }
    } catch (err) {
      setError("Erro ao carregar discos");
      addLog("Erro ao carregar discos");
    }
  };

  // Inicia varredura forense
  const startScan = async () => {
    if (selectedDisk === null) {
      setError("Selecione um disco primeiro");
      return;
    }

    setScanProgress({ status: "scanning", progress: 0 });
    setRecoveredFiles([]);
    addLog(`Iniciando varredura do disco ${selectedDisk}`);

    try {
      const response = await fetch(`${FORENSE_AGENT_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ disk_number: selectedDisk }),
      });

      const data = await response.json();
      if (data.success) {
        setScanProgress({ status: "completed", progress: 100 });
        setRecoveredFiles(data.files || []);
        addLog(`Varredura concluída. Arquivos recuperados: ${data.files?.length || 0}`);
      } else {
        setScanProgress({ status: "error", progress: 0 });
        setError(data.error || "Erro na varredura");
        addLog(`Erro na varredura: ${data.error}`);
      }
    } catch (err) {
      setScanProgress({ status: "error", progress: 0 });
      setError("Erro ao iniciar varredura");
      addLog("Erro ao iniciar varredura");
    }
  };

  // Recupera arquivo específico
  const recoverFile = async (file: RecoveredFile) => {
    addLog(`Recuperando arquivo: ${file.name}`);
    try {
      const response = await fetch(`${FORENSE_AGENT_URL}/recover`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          disk_number: selectedDisk,
          offset: file.offset,
          size: file.size,
        }),
      });

      const data = await response.json();
      if (data.success) {
        // Download do arquivo
        const blob = new Blob([Buffer.from(data.data, "base64")]);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        addLog(`Arquivo recuperado: ${file.name}`);
      } else {
        addLog(`Erro ao recuperar arquivo: ${data.error}`);
      }
    } catch (err) {
      addLog("Erro ao recuperar arquivo");
    }
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${timestamp}] ${message}`]);
  };

  return (
    <div className="investigacao-forense border border-green-500 p-3 mb-3 bg-black">
      <div className="text-green-400 font-mono font-bold mb-3 text-sm">
        [ 5 - INVESTIGAÇÃO FORENSE ]
      </div>

      {/* Status do Agente */}
      <div className="mb-3 border border-green-900 p-3 bg-black">
        <div className="text-green-400 font-mono font-bold mb-2 text-sm">
          [ STATUS DO AGENTE ]
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              agentConnected ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="text-green-400 font-mono text-xs">
            {agentConnected
              ? "AGENTE CONECTADO (localhost:8888)"
              : "AGENTE DESCONECTADO - Inicie o agente local"}
          </span>
        </div>
        {!agentConnected && (
          <div className="mt-2 text-yellow-400 font-mono text-xs">
            [ INSTRUÇÕES: Execute o agente forense (forense_agent.py) como Administrador/Root ]
          </div>
        )}
      </div>

      {/* Seleção de Disco */}
      {agentConnected && (
        <div className="mb-3 border border-green-900 p-3 bg-black">
          <div className="text-green-400 font-mono font-bold mb-2 text-sm">
            [ SELEÇÃO DE DISCO ]
          </div>
          <div className="flex gap-2 mb-2">
            <button
              onClick={loadDisks}
              className="bg-green-900 hover:bg-green-700 text-green-400 font-mono text-xs py-1.5 px-3 border border-green-500 transition-colors"
            >
              [ CARREGAR DISCOS ]
            </button>
          </div>
          {disks.length > 0 && (
            <div className="space-y-1">
              {disks.map((disk) => (
                <div
                  key={disk.number}
                  className={`flex items-center gap-2 p-2 border cursor-pointer transition-colors ${
                    selectedDisk === disk.number
                      ? "border-green-500 bg-green-900/20"
                      : "border-green-900 hover:border-green-500"
                  }`}
                  onClick={() => setSelectedDisk(disk.number)}
                >
                  <input
                    type="radio"
                    checked={selectedDisk === disk.number}
                    onChange={() => setSelectedDisk(disk.number)}
                    className="accent-green-500"
                  />
                  <span className="text-green-400 font-mono text-xs">
                    Disco {disk.number}: {disk.path}
                    {disk.size && ` (${(disk.size / 1024 / 1024 / 1024).toFixed(2)} GB)`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Controles de Varredura */}
      {agentConnected && selectedDisk !== null && (
        <div className="mb-3 border border-green-900 p-3 bg-black">
          <div className="text-green-400 font-mono font-bold mb-2 text-sm">
            [ CONTROLES DE VARREDURA ]
          </div>
          <button
            onClick={startScan}
            disabled={scanProgress.status === "scanning"}
            className="w-full bg-green-900 hover:bg-green-700 disabled:bg-gray-700 text-green-400 font-mono text-sm py-2 px-3 border border-green-500 transition-colors"
          >
            {scanProgress.status === "scanning"
              ? "[ VARRENDO... ]"
              : "[ INICIAR VARREDURA FORENSE ]"}
          </button>

          {/* Barra de Progresso */}
          {scanProgress.status === "scanning" && (
            <div className="mt-2">
              <div className="text-green-400 font-mono text-xs mb-1">
                Progresso: {scanProgress.progress}%
              </div>
              <div className="w-full bg-green-900 border border-green-500 h-2">
                <div
                  className="bg-green-500 h-full transition-all"
                  style={{ width: `${scanProgress.progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Arquivos Recuperados */}
      {recoveredFiles.length > 0 && (
        <div className="mb-3 border border-green-900 p-3 bg-black">
          <div className="text-green-400 font-mono font-bold mb-2 text-sm">
            [ ARQUIVOS RECUPERADOS: {recoveredFiles.length} ]
          </div>
          <div className="space-y-1 max-h-[300px] overflow-y-auto">
            {recoveredFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 border border-green-900 hover:border-green-500 transition-colors"
              >
                <div className="flex-1">
                  <div className="text-green-400 font-mono text-xs">
                    {file.name}
                  </div>
                  <div className="text-green-700 font-mono text-xs">
                    Offset: {file.offset} | Tamanho: {(file.size / 1024).toFixed(2)} KB
                  </div>
                </div>
                <button
                  onClick={() => recoverFile(file)}
                  className="bg-green-900 hover:bg-green-700 text-green-400 font-mono text-xs py-1 px-2 border border-green-500 transition-colors"
                >
                  [ RECUPERAR ]
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Logs */}
      <div className="border border-green-900 p-3 bg-black">
        <div className="text-green-400 font-mono font-bold mb-2 text-sm">
          [ LOGS ]
        </div>
        <div className="bg-black border border-green-900 p-2 h-[150px] overflow-y-auto font-mono text-xs space-y-1">
          {logs.map((log, index) => (
            <div key={index} className="text-green-400">
              {log}
            </div>
          ))}
          {logs.length === 0 && (
            <div className="text-gray-500">Nenhum log disponível</div>
          )}
        </div>
      </div>
    </div>
  );
};

export const InvestigacaoForenseMemo = React.memo(InvestigacaoForense);
