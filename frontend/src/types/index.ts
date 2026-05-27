/**
 * Tipos e Interfaces TypeScript
 * Sistema centralizado de tipagem para KALI-CORE V3
 */

export interface Vulnerabilidade {
  id: number;
  operacao_id: number;
  criticidade: "critica" | "alta" | "media" | "baixa";
  titulo: string;
  descricao: string;
  correcao: string;
  timestamp: string;
  alvo_ip?: string;
  attack_type?: string;
}

export interface Alvo {
  id: number;
  ip_dominio: string;
  timestamp: string;
}

export interface HistoricoOperacao {
  id: number;
  alvo_id: number;
  attack_type: string;
  attack_phase: string;
  payload: string | null;
  success: boolean;
  response_code: number | null;
  response_data: string | null;
  timestamp: string;
}

export interface APIResponse<T> {
  sucesso: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface VulnerabilitiesResponse {
  sucesso: boolean;
  vulnerabilidades: Vulnerabilidade[];
}

export interface TargetsResponse {
  sucesso: boolean;
  targets: string[];
}

export interface AttackTypesResponse {
  sucesso: boolean;
  attack_types: string[];
}

export interface StartOperationRequest {
  target: string;
  taticas: string[];
}

export interface StartOperationResponse {
  sucesso: boolean;
  target: string;
  alvo_id: number;
  operacoes_criadas: number[];
  total_vulnerabilidades: number;
}

export interface RelatorioItem {
  vulnerabilidade: Vulnerabilidade;
  impactoFinanceiro: string;
  gravidadeExecutiva: string;
  planoMitigacao: string;
  custoEstimado: "Baixo" | "Médio" | "Alto";
}

export type Criticidade = "critica" | "alta" | "media" | "baixa";

export const CRITICIDADE_LABELS: Record<Criticidade, string> = {
  critica: "🔴 CRÍTICO",
  alta: "🟠 ALTO",
  media: "🟡 MÉDIO",
  baixa: "🟢 BAIXO",
};

export const CRITICIDADE_CLASSES: Record<Criticidade, string> = {
  critica: "vuln-critical",
  alta: "vuln-high",
  media: "vuln-medium",
  baixa: "vuln-low",
};
