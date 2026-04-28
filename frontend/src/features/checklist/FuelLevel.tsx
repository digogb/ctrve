import { Controller, type Control, type FieldError } from "react-hook-form";
import type { ChecklistEntregaData } from "./checklistSchema";

const FUEL_OPTIONS = ["1/4", "2/4", "3/4", "4/4"] as const;

interface FuelLevelProps {
  control: Control<ChecklistEntregaData>;
  error?: FieldError;
  className?: string;
}

export default function FuelLevel({ control, error, className = "mt-6" }: FuelLevelProps) {
  return (
    <section className={className}>
      <h3 className="mb-3 text-lg font-semibold">Nível de Combustível</h3>
      <Controller
        name="nivel_combustivel"
        control={control}
        render={({ field }) => (
          <div className="flex gap-3">
            {FUEL_OPTIONS.map((option) => (
              <label
                key={option}
                className={`flex cursor-pointer items-center justify-center rounded-md border px-4 py-2 text-sm font-medium transition-colors ${
                  field.value === option
                    ? "border-primary bg-primary text-white"
                    : "border-border bg-white hover:border-primary/50"
                }`}
              >
                <input
                  type="radio"
                  id={`fuel-${option}`}
                  value={option}
                  checked={field.value === option}
                  onChange={() => field.onChange(option)}
                  className="sr-only"
                />
                {option}
              </label>
            ))}
          </div>
        )}
      />
      {error && (
        <p role="alert" className="mt-2 text-sm text-danger">{error.message}</p>
      )}
    </section>
  );
}
