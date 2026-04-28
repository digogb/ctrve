import type { ChecklistResponse } from "../types/checklist";

interface StatusBadgeProps {
  status: ChecklistResponse["status"];
  isLocked: boolean;
}

export default function StatusBadge({ status, isLocked }: StatusBadgeProps) {
  if (!isLocked) {
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        Em preenchimento
      </span>
    );
  }
  if (status === "devolvido") {
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700 border border-green-200">
        Devolvido
      </span>
    );
  }
  return (
    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
      Entregue
    </span>
  );
}
