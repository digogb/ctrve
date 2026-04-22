export type UserRole = "responsavel" | "motorista";

export interface User {
  id: number;
  username: string;
  full_name: string;
  matricula: string;
  role: UserRole;
  is_active: boolean;
}
