import { z } from "zod";

export const checklistInfoSchema = z.object({
  // P-5: preprocess garante uppercase antes do regex, aceitando input em minúsculo
  placa: z.preprocess(
    (val) => (typeof val === "string" ? val.toUpperCase() : val),
    z
      .string()
      .min(1, "Informe a placa do veículo")
      .regex(
        /^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}-[0-9]{4}$/,
        "Formato de placa inválido. Informe no formato Mercosul (ABC1D23) ou antigo (ABC-1234)."
      )
  ),
  unidade: z.string().min(1, "Informe a unidade"),
  subunidade: z.string().optional(),
  motorista: z.string().min(1, "Informe o nome do motorista"),
  matricula_motorista: z
    .string()
    .min(1, "Informe a matrícula do motorista")
    .regex(/^\d+$/, "O campo Matrícula aceita apenas valores numéricos."),
  quilometragem_inicial: z.coerce
    .number({ invalid_type_error: "Informe a quilometragem inicial" })
    .min(0, "Quilometragem não pode ser negativa"),
});

export type ChecklistInfoData = z.infer<typeof checklistInfoSchema>;

export const checklistItemSchema = z.object({
  nome: z.string(),
  status: z.enum(["ok", "nao_ok"], { message: "Selecione OK ou Não OK para este item." }),
});

export const damagePointSchema = z.object({
  x: z.number().min(0).max(100),
  y: z.number().min(0).max(100),
  vista: z.enum(["topo", "lateral_esquerda", "lateral_direita", "frontal_traseira"]),
  tipo: z.enum(["risco", "amassado", "trincado"], {
    message:
      "Selecione o tipo de avaria (Risco, Amassado ou Trincado) para cada ponto marcado no mapa do veículo.",
  }),
});

export const checklistEntregaSchema = z.object({
  itens: z.array(checklistItemSchema).length(20),
  nivel_combustivel: z.enum(["1/4", "2/4", "3/4", "4/4"], {
    message: "Selecione o nível de combustível do veículo (1/4, 2/4, 3/4 ou 4/4).",
  }),
  data_entrega: z
    .string()
    .min(1, "Informe a data e o horário da entrega.")
    .refine((v) => !isNaN(new Date(v).getTime()), "Data e horário inválidos.")
    .transform((v) => new Date(v).toISOString()),
  avarias: z.array(damagePointSchema).default([]),
});

export type ChecklistEntregaData = z.infer<typeof checklistEntregaSchema>;
