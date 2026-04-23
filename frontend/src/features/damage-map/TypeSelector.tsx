import { useEffect, useRef } from "react";
import type { TipoAvaria } from "../../types/damage";

interface TypeSelectorProps {
  x: number;
  y: number;
  onSelect: (tipo: TipoAvaria) => void;
  onCancel: () => void;
}

const TIPOS: { value: TipoAvaria; label: string; color: string }[] = [
  { value: "risco", label: "Risco", color: "#EF4444" },
  { value: "amassado", label: "Amassado", color: "#F97316" },
  { value: "trincado", label: "Trincado", color: "#3B82F6" },
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
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y}%`,
        transform: "translate(-50%, -100%)",
        background: "white",
        border: "1px solid #ccc",
        borderRadius: 6,
        padding: 4,
        display: "flex",
        gap: 4,
        zIndex: 10,
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
      }}
    >
      {TIPOS.map((t) => (
        <button
          key={t.value}
          type="button"
          name="tipo-avaria"
          onClick={() => onSelect(t.value)}
          style={{
            background: t.color,
            color: "white",
            border: "none",
            borderRadius: 4,
            padding: "4px 8px",
            cursor: "pointer",
            fontSize: 12,
          }}
        >
          {t.label}
        </button>
      ))}
      <button
        type="button"
        onClick={onCancel}
        style={{
          background: "#6B7280",
          color: "white",
          border: "none",
          borderRadius: 4,
          padding: "4px 8px",
          cursor: "pointer",
          fontSize: 12,
        }}
      >
        Cancelar
      </button>
    </div>
  );
}
