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
