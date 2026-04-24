import { useEffect, useState } from "react";
import type { DamagePoint, TipoAvaria, VistaVeiculo } from "../../types/damage";
import TypeSelector from "./TypeSelector";

interface VehicleViewProps {
  vista: VistaVeiculo;
  label: string;
  points: DamagePoint[];
  onAddPoint: (x: number, y: number, tipo: TipoAvaria) => void;
  onRemovePoint: (index: number) => void;
  readOnly?: boolean;
}

const DAMAGE_COLORS: Record<TipoAvaria, string> = {
  risco: "#EF4444",
  amassado: "#F97316",
  trincado: "#3B82F6",
};

function TopView() {
  return (
    <>
      <rect x="75" y="10" width="150" height="280" rx="30" ry="30" fill="#E5E7EB" stroke="#374151" strokeWidth="2" />
      <rect x="95" y="35" width="110" height="60" rx="8" fill="#D1D5DB" stroke="#6B7280" strokeWidth="1" />
      <rect x="95" y="205" width="110" height="50" rx="8" fill="#D1D5DB" stroke="#6B7280" strokeWidth="1" />
      <text x="150" y="25" textAnchor="middle" fontSize="10" fill="#6B7280">Frente</text>
      <text x="150" y="285" textAnchor="middle" fontSize="10" fill="#6B7280">Traseira</text>
    </>
  );
}

function LeftView() {
  return (
    <>
      <path
        d="M30,200 L30,180 Q30,160 50,150 L80,130 Q100,100 120,95 L200,90 Q230,90 240,100 L260,130 L270,150 L270,200 Z"
        fill="#E5E7EB" stroke="#374151" strokeWidth="2"
      />
      <circle cx="70" cy="200" r="22" fill="#9CA3AF" stroke="#374151" strokeWidth="2" />
      <circle cx="240" cy="200" r="22" fill="#9CA3AF" stroke="#374151" strokeWidth="2" />
      <rect x="90" y="105" width="100" height="50" rx="5" fill="#D1D5DB" stroke="#6B7280" strokeWidth="1" />
    </>
  );
}

function RightView() {
  return (
    <>
      <path
        d="M270,200 L270,180 Q270,160 250,150 L220,130 Q200,100 180,95 L100,90 Q70,90 60,100 L40,130 L30,150 L30,200 Z"
        fill="#E5E7EB" stroke="#374151" strokeWidth="2"
      />
      <circle cx="230" cy="200" r="22" fill="#9CA3AF" stroke="#374151" strokeWidth="2" />
      <circle cx="60" cy="200" r="22" fill="#9CA3AF" stroke="#374151" strokeWidth="2" />
      <rect x="110" y="105" width="100" height="50" rx="5" fill="#D1D5DB" stroke="#6B7280" strokeWidth="1" />
    </>
  );
}

function FrontRearView() {
  return (
    <>
      <rect x="60" y="30" width="180" height="200" rx="20" ry="20" fill="#E5E7EB" stroke="#374151" strokeWidth="2" />
      <rect x="80" y="50" width="140" height="60" rx="10" fill="#D1D5DB" stroke="#6B7280" strokeWidth="1" />
      <circle cx="85" cy="140" r="12" fill="#FBBF24" stroke="#374151" strokeWidth="1.5" />
      <circle cx="215" cy="140" r="12" fill="#FBBF24" stroke="#374151" strokeWidth="1.5" />
      <rect x="100" y="160" width="100" height="15" rx="4" fill="#D1D5DB" stroke="#6B7280" strokeWidth="1" />
    </>
  );
}

const VIEW_COMPONENTS: Record<VistaVeiculo, () => JSX.Element> = {
  topo: TopView,
  lateral_esquerda: LeftView,
  lateral_direita: RightView,
  frontal_traseira: FrontRearView,
};

const VIEW_LABELS: Record<VistaVeiculo, string> = {
  topo: "Topo",
  lateral_esquerda: "Lateral Esquerda",
  lateral_direita: "Lateral Direita",
  frontal_traseira: "Frontal / Traseira",
};

export { VIEW_LABELS };

export default function VehicleView({
  vista,
  label,
  points,
  onAddPoint,
  onRemovePoint,
  readOnly,
}: VehicleViewProps) {
  const [pendingPoint, setPendingPoint] = useState<{ x: number; y: number } | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    setSelectedIndex(null);
  }, [points.length]);

  const handleSvgClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (readOnly) return;
    if (selectedIndex !== null) {
      setSelectedIndex(null);
      return;
    }
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setPendingPoint({ x, y });
  };

  const handleTypeSelect = (tipo: TipoAvaria) => {
    if (pendingPoint) {
      onAddPoint(pendingPoint.x, pendingPoint.y, tipo);
    }
    setPendingPoint(null);
  };

  const handlePointClick = (e: React.MouseEvent, index: number) => {
    if (readOnly) return;
    e.stopPropagation();
    setSelectedIndex(selectedIndex === index ? null : index);
  };

  const handleRemove = (index: number) => {
    onRemovePoint(index);
    setSelectedIndex(null);
  };

  const ViewComponent = VIEW_COMPONENTS[vista];

  return (
    <div data-testid={`vehicle-view-${vista}`}>
      <h3 className="mb-1 text-center text-sm font-medium">{label}</h3>
      <div className="relative">
        <svg
          viewBox="0 0 300 300"
          width="100%"
          className={`block rounded-lg border border-border ${readOnly ? "cursor-default" : "cursor-crosshair"}`}
          onClick={handleSvgClick}
          aria-label={label}
          role="img"
        >
          <ViewComponent />
          {points.map((point, i) => (
            <circle
              key={i}
              cx={(point.x / 100) * 300}
              cy={(point.y / 100) * 300}
              r={8}
              fill={DAMAGE_COLORS[point.tipo]}
              stroke="white"
              strokeWidth="2"
              style={{ cursor: readOnly ? "default" : "pointer" }}
              onClick={(e) => handlePointClick(e, i)}
              data-testid={`damage-point-${vista}-${i}`}
            />
          ))}
        </svg>

        {!readOnly && pendingPoint && (
          <TypeSelector
            x={pendingPoint.x}
            y={pendingPoint.y}
            onSelect={handleTypeSelect}
            onCancel={() => setPendingPoint(null)}
          />
        )}

        {!readOnly && selectedIndex !== null && points[selectedIndex] && (
          <div
            className="absolute z-10 rounded-md border border-border bg-white p-1 shadow-lg"
            style={{
              left: `${points[selectedIndex].x}%`,
              top: `${points[selectedIndex].y}%`,
              transform: "translate(-50%, -100%)",
            }}
          >
            <button
              type="button"
              onClick={() => handleRemove(selectedIndex)}
              className="rounded bg-danger px-2 py-1 text-xs text-white hover:bg-danger-dark"
            >
              Remover
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
