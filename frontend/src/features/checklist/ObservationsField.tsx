import { type UseFormRegisterReturn } from "react-hook-form";
import { Label } from "@/components/ui/label";

interface ObservationsFieldProps {
  register: UseFormRegisterReturn;
  label?: string;
}

export default function ObservationsField({ register, label = "Observações" }: ObservationsFieldProps) {
  return (
    <div className="mt-6 space-y-2">
      <Label htmlFor={register.name}>{label}</Label>
      <textarea
        id={register.name}
        rows={4}
        className="w-full rounded-md border border-border bg-white p-2 text-sm"
        placeholder="Registre observações sobre avarias ou situações relevantes (opcional)"
        {...register}
      />
    </div>
  );
}
