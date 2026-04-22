export type ChecklistStatus = "entregue" | "devolvido";

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
  created_at: string;
}
