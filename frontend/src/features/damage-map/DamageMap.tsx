import type { DamagePoint, TipoAvaria, VistaVeiculo } from "../../types/damage";
import VehicleView, { VIEW_LABELS } from "./VehicleView";

interface DamageMapProps {
  value: DamagePoint[];
  onChange: (points: DamagePoint[]) => void;
  readOnly?: boolean;
}

const VISTAS: VistaVeiculo[] = ["topo", "lateral_esquerda", "lateral_direita", "frontal_traseira"];

export default function DamageMap({ value, onChange, readOnly }: DamageMapProps) {
  const handleAddPoint = (vista: VistaVeiculo, x: number, y: number, tipo: TipoAvaria) => {
    onChange([...value, { x, y, vista, tipo }]);
  };

  const handleRemovePoint = (vista: VistaVeiculo, localIndex: number) => {
    let count = 0;
    const globalIndex = value.findIndex((p) => {
      if (p.vista === vista) {
        if (count === localIndex) return true;
        count++;
      }
      return false;
    });
    if (globalIndex !== -1) {
      onChange(value.filter((_, i) => i !== globalIndex));
    }
  };

  return (
    <section aria-label="Mapa de Avarias" data-testid="damage-map">
      <h2 style={{ fontSize: 16, marginBottom: 8 }}>Mapa de Avarias</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
        }}
      >
        {VISTAS.map((vista) => (
          <VehicleView
            key={vista}
            vista={vista}
            label={VIEW_LABELS[vista]}
            points={value.filter((p) => p.vista === vista)}
            onAddPoint={(x, y, tipo) => handleAddPoint(vista, x, y, tipo)}
            onRemovePoint={(localIndex) => handleRemovePoint(vista, localIndex)}
            readOnly={readOnly}
          />
        ))}
      </div>
    </section>
  );
}
