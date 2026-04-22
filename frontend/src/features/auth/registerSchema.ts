import { z } from "zod";

const passwordSchema = z
  .string()
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
    "A senha deve conter no mínimo 8 caracteres, incluindo ao menos uma letra maiúscula, uma letra minúscula e um número."
  );

export const registerSchema = z
  .object({
    full_name: z.string().min(1, "Informe o nome completo"),
    matricula: z.string().min(1, "Informe a matrícula"),
    username: z.string().min(1, "Informe o nome de usuário"),
    role: z.enum(["responsavel", "motorista"], {
      errorMap: () => ({ message: "Selecione um perfil" }),
    }),
    password: passwordSchema,
    confirmPassword: z.string().min(1, "Confirme a senha"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "As senhas não coincidem",
    path: ["confirmPassword"],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;
