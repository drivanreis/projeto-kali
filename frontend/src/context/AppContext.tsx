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
  Alvo,
  VulnerabilitiesResponse,
  TargetsResponse,
  AttackTypesResponse,
  StartOperationResponse,
  StartOperationRequest,
} from "@/types";

const API_BASE = "http://127.0.0.1:8001";

interface AppContextType {
  vulnerabilidades: Vulnerabilidade[];
  alvos: string[];
  attackTypes: string[];
  carregando: boolean;
  erro: string | null;
  filtroAlvo: string;
  filtroAtaque: string;
  setFiltroAlvo: (alvo: string) => void;
  setFiltroAtaque: (ataque: string) => void;
  iniciarOperacao: (target: string, taticas: string[]) => Promise<StartOperationResponse | null>;
  atualizarVulnerabilidades: () => Promise<void>;
  carregarFiltros: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [vulnerabilidades, setVulnerabilidades] = useState<Vulnerabilidade[]>([]);
  const [alvos, setAlvos] = useState<string[]>([]);
  const [attackTypes, setAttackTypes] = useState<string[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [filtroAlvo, setFiltroAlvo] = useState("");
  const [filtroAtaque, setFiltroAtaque] = useState("");

  const atualizarVulnerabilidades = useCallback(async (): Promise<void> => {
    try {
      setCarregando(true);
      const params: Record<string, string> = {};
      if (filtroAlvo) params.alvo_ip = filtroAlvo;
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
  }, [filtroAlvo, filtroAtaque]);

  const carregarFiltros = useCallback(async (): Promise<void> => {
    try {
      const [targetRes, tiposRes] = await Promise.all([
        axiosInstance.get<TargetsResponse>("/api/targets"),
        axiosInstance.get<AttackTypesResponse>("/api/attack-types"),
      ]);

      if (targetRes.data.sucesso && tiposRes.data.sucesso) {
        setAlvos(targetRes.data.targets || []);
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
        const payload: StartOperationRequest = { target, taticas };
        const response = await axiosInstance.post<StartOperationResponse>("/api/start", payload);

        if (response.data.sucesso) {
          setErro(null);
          await carregarFiltros();
          await atualizarVulnerabilidades();
          return response.data;
        } else {
          setErro("Falha ao iniciar operação");
          return null;
        }
      } catch (err) {
        console.error("Erro ao iniciar operação:", err);
        setErro(err instanceof Error ? err.message : "Erro desconhecido ao iniciar operação");
        return null;
      } finally {
        setCarregando(false);
      }
    },
    [carregarFiltros, atualizarVulnerabilidades]
  );

  useEffect(() => {
    const interval = setInterval(() => {
      void atualizarVulnerabilidades();
    }, 2000);

    return () => clearInterval(interval);
  }, [atualizarVulnerabilidades]);

  const value: AppContextType = {
    vulnerabilidades,
    alvos,
    attackTypes,
    carregando,
    erro,
    filtroAlvo,
    filtroAtaque,
    setFiltroAlvo,
    setFiltroAtaque,
    iniciarOperacao,
    atualizarVulnerabilidades,
    carregarFiltros,
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
