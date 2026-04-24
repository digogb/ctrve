import { useEffect, useRef } from "react";
import type { TipoAvaria } from "../../types/damage";

interface TypeSelectorProps {
  x: number;
  y: number;
  onSelect: (tipo: TipoAvaria) => void;
  onCancel: () => void;
}

const TIPOS: { value: TipoAvaria; label: string; color: string }[] = [
  { value: "risco", label: "Risco", color: "bg-risco" },
  { value: "amassado", label: "Amassado", color: "bg-amassado" },
  { value: "trincado", label: "Trincado", color: "bg-trincado" },
];

export default function TypeSelector({ x, y, onSelect, onCancel }: TypeSelectorProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onCancel();
      }
    }
    document.addEventListener("pointerdown", handleClickOutside);
    return () => document.removeEventListener("pointerdown", handleClickOutside);
  }, [onCancel]);

  return (
    <div
      ref={ref}
      role="group"
      aria-label="Selecione o tipo de avaria"
      className="absolute z-10 flex gap-1 rounded-md border border-border bg-white p-1 shadow-lg"
      style={{
        left: `${x}%`,
        top: `${y}%`,
        transform: "translate(-50%, -100%)",
      }}
    >
      {TIPOS.map((t) => (
        <button
          key={t.value}
          type="button"
          name="tipo-avaria"
          onClick={() => onSelect(t.value)}
          className={`${t.color} rounded px-2 py-1 text-xs text-white hover:opacity-80`}
        >
          {t.label}
        </button>
      ))}
      <button
        type="button"
        onClick={onCancel}
        className="rounded bg-muted px-2 py-1 text-xs text-white hover:opacity-80"
      >
        Cancelar
      </button>
    </div>
  );
}
