export type TipoAvaria = "risco" | "amassado" | "trincado";
export type VistaVeiculo = "topo" | "lateral_esquerda" | "lateral_direita" | "frontal_traseira";

export interface DamagePoint {
  x: number;
  y: number;
  vista: VistaVeiculo;
  tipo: TipoAvaria;
}
