import { useState } from "react";
import type { DamagePoint, TipoAvaria, VistaVeiculo } from "../../types/damage";
import TypeSelector from "./TypeSelector";

interface DamageMapProps {
  value: DamagePoint[];
  onChange: (points: DamagePoint[]) => void;
  readOnly?: boolean;
}

const DAMAGE_COLORS: Record<TipoAvaria, string> = {
  risco: "#EF4444",
  amassado: "#F97316",
  trincado: "#3B82F6",
};

const DAMAGE_LABELS: Record<TipoAvaria, string> = {
  risco: "Risco",
  amassado: "Amassado",
  trincado: "Trincado",
};

// Limiar Y (%) que separa a vista de topo da vista lateral na imagem
const TOPO_THRESHOLD = 45;

function inferVista(y: number): VistaVeiculo {
  return y < TOPO_THRESHOLD ? "topo" : "lateral_esquerda";
}

export default function DamageMap({ value, onChange, readOnly }: DamageMapProps) {
  const [pending, setPending] = useState<{ x: number; y: number } | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (readOnly) return;
    if (selected !== null) { setSelected(null); return; }
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setPending({ x, y });
  };

  const handleTypeSelect = (tipo: TipoAvaria) => {
    if (!pending) return;
    const vista = inferVista(pending.y);
    onChange([...value, { x: pending.x, y: pending.y, vista, tipo }]);
    setPending(null);
  };

  const handlePointClick = (e: React.MouseEvent, index: number) => {
    if (readOnly) return;
    e.stopPropagation();
    setSelected(selected === index ? null : index);
  };

  const handleRemove = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
    setSelected(null);
  };

  return (
    <section aria-label="Mapa de Avarias" data-testid="damage-map">
      <h2 className="mb-2 text-base font-semibold">Mapa de Avarias</h2>

      <div
        className={`relative w-full overflow-hidden rounded-lg border border-border bg-white ${readOnly ? "cursor-default" : "cursor-crosshair"}`}
        onClick={handleClick}
      >
        <img
          src="/marcacao.png"
          alt="Mapa de avarias do veículo"
          className="block w-full select-none"
          draggable={false}
        />

        {/* Pontos de avaria */}
        {value.map((point, i) => (
          <button
            key={i}
            type="button"
            data-testid={`damage-point-${point.vista}-${i}`}
            onClick={(e) => handlePointClick(e, i)}
            title={`${DAMAGE_LABELS[point.tipo]} — clique para remover`}
            className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow-md transition-transform hover:scale-110 focus:outline-none"
            style={{
              left: `${point.x}%`,
              top: `${point.y}%`,
              width: 20,
              height: 20,
              background: DAMAGE_COLORS[point.tipo],
              cursor: readOnly ? "default" : "pointer",
            }}
            aria-label={`Avaria ${DAMAGE_LABELS[point.tipo]}`}
          />
        ))}

        {/* Popup de remoção */}
        {!readOnly && selected !== null && value[selected] && (
          <div
            className="absolute z-20 rounded-md border border-border bg-white p-1 shadow-lg"
            style={{
              left: `${value[selected].x}%`,
              top: `${value[selected].y}%`,
              transform: "translate(-50%, -130%)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <p className="mb-1 px-1 text-xs font-medium text-muted">
              {DAMAGE_LABELS[value[selected].tipo]}
            </p>
            <button
              type="button"
              onClick={() => handleRemove(selected)}
              className="rounded bg-danger px-2 py-1 text-xs text-white hover:bg-danger-dark"
            >
              Remover
            </button>
          </div>
        )}

        {/* TypeSelector ao adicionar ponto */}
        {!readOnly && pending && (
          <div onClick={(e) => e.stopPropagation()}>
            <TypeSelector
              x={pending.x}
              y={pending.y}
              onSelect={handleTypeSelect}
              onCancel={() => setPending(null)}
            />
          </div>
        )}
      </div>

      {/* Legenda */}
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted">
        {(Object.entries(DAMAGE_COLORS) as [TipoAvaria, string][]).map(([tipo, color]) => (
          <span key={tipo} className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-full border border-white shadow-sm" style={{ background: color }} />
            {DAMAGE_LABELS[tipo]}
          </span>
        ))}
        {!readOnly && <span className="ml-auto italic">Clique no mapa para marcar uma avaria</span>}
      </div>
    </section>
  );
}
