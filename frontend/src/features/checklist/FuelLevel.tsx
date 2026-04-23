import { Controller, type Control, type FieldError } from "react-hook-form";
import type { ChecklistEntregaData } from "./checklistSchema";

const FUEL_OPTIONS = ["1/4", "2/4", "3/4", "4/4"] as const;

interface FuelLevelProps {
  control: Control<ChecklistEntregaData>;
  error?: FieldError;
}

export default function FuelLevel({ control, error }: FuelLevelProps) {
  return (
    <section className="fuel-level">
      <h3>Nível de Combustível</h3>
      <Controller
        name="nivel_combustivel"
        control={control}
        render={({ field }) => (
          <div className="fuel-options">
            {FUEL_OPTIONS.map((option) => (
              <label key={option} className="fuel-option">
                <input
                  type="radio"
                  id={`fuel-${option}`}
                  value={option}
                  checked={field.value === option}
                  onChange={() => field.onChange(option)}
                />
                {option}
              </label>
            ))}
          </div>
        )}
      />
      {error && (
        <p role="alert" className="field-error">
          {error.message}
        </p>
      )}
    </section>
  );
}
