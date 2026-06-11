import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import axios, { AxiosInstance } from "axios";
import {
  Vulnerabilidade,
  VulnerabilitiesResponse,
  TargetsResponse,
  AttackTypesResponse,
  StartOperationResponse,
  StartOperationRequest,
} from "@/types";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "SUCCESS";
  message: string;
}

const API_BASE = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:5190`;

interface AppContextType {
  vulnerabilidades: Vulnerabilidade[];
  clientesIps: string[];
  attackTypes: string[];
  carregando: boolean;
  erro: string | null;
  filtroCliente: string;
  filtroAtaque: string;
  logs: LogEntry[];
  setFiltroCliente: (cliente: string) => void;
  setFiltroAtaque: (ataque: string) => void;
  iniciarOperacao: (target: string, taticas: string[]) => Promise<StartOperationResponse | null>;
  atualizarVulnerabilidades: () => Promise<void>;
  carregarFiltros: () => Promise<void>;
  addLog: (level: "INFO" | "WARNING" | "ERROR" | "SUCCESS", message: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [vulnerabilidades, setVulnerabilidades] = useState<Vulnerabilidade[]>([]);
  const [clientesIps, setClientesIps] = useState<string[]>([]);
  const [attackTypes, setAttackTypes] = useState<string[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [filtroCliente, setFiltroCliente] = useState("");
  const [filtroAtaque, setFiltroAtaque] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const addLog = useCallback((level: "INFO" | "WARNING" | "ERROR" | "SUCCESS", message: string) => {
    const timestamp = new Date().toLocaleTimeString("pt-BR");
    setLogs((prev) => [...prev, { timestamp, level, message }]);
  }, []);

  const atualizarVulnerabilidades = useCallback(async (): Promise<void> => {
    try {
      setCarregando(true);
      const params: Record<string, string> = {};
      if (filtroCliente) params.alvo_ip = filtroCliente;
      if (filtroAtaque) params.attack_type = filtroAtaque;

      const response = await axiosInstance.get<VulnerabilitiesResponse>("/api/vulnerabilidades", {
        params,
      });

      if (response.data.sucesso) {
        setVulnerabilidades(response.data.vulnerabilidades || []);
        setErro(null);
      } else {
        setErro("Falha ao carregar vulnerabilidades");
      }
    } catch (err) {
      console.error("Erro ao atualizar vulnerabilidades:", err);
      setErro(
        err instanceof Error ? err.message : "Erro desconhecido ao carregar vulnerabilidades"
      );
    } finally {
      setCarregando(false);
    }
  }, [filtroCliente, filtroAtaque]);

  const carregarFiltros = useCallback(async (): Promise<void> => {
    try {
      const [targetRes, tiposRes] = await Promise.all([
        axiosInstance.get<TargetsResponse>("/api/targets"),
        axiosInstance.get<AttackTypesResponse>("/api/attack-types"),
      ]);

      if (targetRes.data.sucesso && tiposRes.data.sucesso) {
        setClientesIps(targetRes.data.targets || []);
        setAttackTypes(tiposRes.data.attack_types || []);
      }
    } catch (err) {
      console.error("Erro ao carregar filtros:", err);
    }
  }, []);

  const iniciarOperacao = useCallback(
    async (target: string, taticas: string[]): Promise<StartOperationResponse | null> => {
      try {
        setCarregando(true);
        addLog("INFO", `Iniciando operação para cliente: ${target}`);
        addLog("INFO", `Táticas selecionadas: ${taticas.join(", ")}`);
        
        const payload: StartOperationRequest = { target, taticas };
        const response = await axiosInstance.post<StartOperationResponse>("/api/start", payload);

        if (response.data.sucesso) {
          setErro(null);
          addLog("SUCCESS", `Operação iniciada com sucesso. Cliente ID: ${response.data.alvo_id}`);
          addLog("INFO", `Operações criadas: ${response.data.operacoes_criadas?.length || 0}`);
          addLog("INFO", `Total de vulnerabilidades: ${response.data.total_vulnerabilidades || 0}`);
          
          await carregarFiltros();
          await atualizarVulnerabilidades();
          return response.data;
        } else {
          setErro("Falha ao iniciar operação");
          addLog("ERROR", "Falha ao iniciar operação no backend");
          return null;
        }
      } catch (err) {
        console.error("Erro ao iniciar operação:", err);
        setErro(err instanceof Error ? err.message : "Erro desconhecido ao iniciar operação");
        addLog("ERROR", `Erro ao iniciar operação: ${err instanceof Error ? err.message : "Erro desconhecido"}`);
        return null;
      } finally {
        setCarregando(false);
        addLog("INFO", "Operação finalizada");
      }
    },
    [carregarFiltros, atualizarVulnerabilidades, addLog]
  );

  useEffect(() => {
    // Carrega vulnerabilidades apenas na montagem
    void atualizarVulnerabilidades();
  }, [atualizarVulnerabilidades]);

  const value: AppContextType = {
    vulnerabilidades,
    clientesIps,
    attackTypes,
    carregando,
    erro,
    filtroCliente,
    filtroAtaque,
    logs,
    setFiltroCliente,
    setFiltroAtaque,
    iniciarOperacao,
    atualizarVulnerabilidades,
    carregarFiltros,
    addLog,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp deve ser usado dentro de um AppProvider");
  }
  return context;
};
