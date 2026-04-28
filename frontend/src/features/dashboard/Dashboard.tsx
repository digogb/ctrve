import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuthContext } from "../auth/AuthContext";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";
import { Badge } from "@/components/ui/badge";

const STATUS_CONFIG = {
  em_preenchimento: { label: "Em preenchimento", color: "bg-amber-400" },
  entregue: { label: "Entregue", color: "bg-blue-500" },
  devolvido: { label: "Devolvido", color: "bg-green-600" },
} satisfies Record<string, { label: string; color: string }>;

export default function Dashboard() {
  const { user } = useAuthContext();

  const { data: checklists = [] } = useQuery<ChecklistResponse[]>({
    queryKey: ["checklists"],
    queryFn: () =>
      apiClient.get<ChecklistResponse[]>("/v1/checklists").then((r) => r.data),
  });

  const now = new Date();
  const emPreenchimento = checklists.filter((c) => !c.is_locked).length;
  const esteMes = checklists.filter(
    (c) =>
      new Date(c.created_at).getMonth() === now.getMonth() &&
      new Date(c.created_at).getFullYear() === now.getFullYear()
  ).length;
  const total = checklists.length;
  const recentes = [...checklists]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3);

  const greeting = user ? `Olá, ${user.full_name.split(" ")[0]}` : "Olá";
  const dateLabel = now.toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div>
      <div className="bg-gradient-to-br from-[#003366] to-[#004080] pb-8">
        <div className="mx-auto max-w-5xl px-6 pt-6">
          <h1 className="text-2xl font-bold text-white">{greeting}</h1>
          <p className="text-blue-200 text-sm mt-1 capitalize">{dateLabel}</p>

          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-white">{emPreenchimento}</p>
              <p className="text-xs text-blue-200 mt-1">Em preenchimento</p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-white">{esteMes}</p>
              <p className="text-xs text-blue-200 mt-1">Total do mês</p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-white">{total}</p>
              <p className="text-xs text-blue-200 mt-1">Total geral</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-6 -mt-4 pb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <Link
            to="/checklists/new"
            className="flex items-center gap-3 rounded-xl bg-primary p-4 text-white shadow-md hover:bg-primary-dark transition"
          >
            <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center text-xl font-bold">
              +
            </div>
            <div>
              <p className="font-semibold text-base">Novo Checklist</p>
              <p className="text-xs text-blue-100">Iniciar preenchimento</p>
            </div>
          </Link>

          <Link
            to="/checklists"
            className="flex items-center gap-3 rounded-xl bg-white border border-border p-4 shadow-md hover:bg-surface transition"
          >
            <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center text-xl">
              🔍
            </div>
            <div>
              <p className="font-semibold text-base text-foreground">Buscar por Placa</p>
              <p className="text-xs text-muted">Consultar checklist existente</p>
            </div>
          </Link>
        </div>

        {recentes.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-muted mb-3 uppercase tracking-wide">
              Recentes
            </h2>
            <div className="space-y-3">
              {recentes.map((c) => {
                const config = STATUS_CONFIG[c.status] ?? { label: c.status, color: "bg-gray-400" };
                return (
                  <Link
                    key={c.id}
                    to={`/checklists/${c.id}`}
                    className="flex items-center gap-4 rounded-xl bg-white border border-border p-4 shadow-sm hover:shadow-md transition"
                  >
                    <div className={`w-2 h-10 rounded-full ${config.color}`} />
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm truncate">{c.placa}</p>
                      <p className="text-xs text-muted">Nº {c.id} · {new Date(c.created_at).toLocaleDateString("pt-BR")}</p>
                    </div>
                    <Badge variant="outline" className="shrink-0 text-xs">
                      {config.label}
                    </Badge>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
