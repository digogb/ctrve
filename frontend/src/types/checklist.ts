import type { DamagePoint } from "./damage";

export type ChecklistStatus = "entregue" | "devolvido";
export type ChecklistItemStatus = "ok" | "nao_ok";
export type NivelCombustivel = "1/4" | "2/4" | "3/4" | "4/4";

export interface ChecklistItemData {
  nome: string;
  status: ChecklistItemStatus | null;
}

export interface ChecklistResponse {
  id: number;
  placa: string;
  unidade: string;
  subunidade: string | null;
  motorista: string;
  matricula_motorista: string;
  quilometragem_inicial: number;
  status: ChecklistStatus;
  is_locked: boolean;
  itens: ChecklistItemData[] | null;
  nivel_combustivel: NivelCombustivel | null;
  data_entrega: string | null;
  avarias: DamagePoint[] | null;
  assinatura_responsavel: string | null;
  assinatura_motorista: string | null;
  quilometragem_final: number | null;
  data_devolucao: string | null;
  itens_devolucao: ChecklistItemData[] | null;
  nivel_combustivel_devolucao: NivelCombustivel | null;
  assinatura_responsavel_devolucao: string | null;
  assinatura_motorista_devolucao: string | null;
  observacoes: string | null;
  observacoes_devolucao: string | null;
  created_at: string;
}
