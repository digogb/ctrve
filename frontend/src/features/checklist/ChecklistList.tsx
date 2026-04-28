import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import StatusBadge from "../../components/StatusBadge";

const MSG_009 =
  "Nenhum checklist encontrado para a placa informada. Verifique o número da placa e tente novamente.";

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "—";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}

function StatusIcon({ isLocked, status }: { isLocked: boolean; status: ChecklistResponse["status"] }) {
  const bg = !isLocked ? "bg-amber-50" : status === "devolvido" ? "bg-green-50" : "bg-blue-50";
  const color = !isLocked ? "text-amber-500" : status === "devolvido" ? "text-green-600" : "text-blue-600";
  return (
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${bg}`}>
      <svg xmlns="http://www.w3.org/2000/svg" className={`size-5 ${color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    </div>
  );
}

async function fetchChecklists(placa: string): Promise<ChecklistResponse[]> {
  const url = placa
    ? `/v1/checklists?placa=${encodeURIComponent(placa)}`
    : "/v1/checklists";
  const { data } = await apiClient.get<ChecklistResponse[]>(url);
  return data;
}

export default function ChecklistList() {
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const { data = [], isLoading } = useQuery<ChecklistResponse[]>({
    queryKey: ["checklists", { placa: searchTerm }],
    queryFn: () => fetchChecklists(searchTerm),
    staleTime: 30 * 1000,
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setSearchTerm(inputValue.trim());
  };

  const showEmpty = !isLoading && searchTerm !== "" && data.length === 0;

  return (
    <div className="mx-auto max-w-3xl p-4">
      <h1 className="mb-6 text-2xl font-bold">Buscar Checklist</h1>

      <form onSubmit={handleSubmit} className="mb-6 flex items-end gap-3">
        <div className="flex-1 space-y-2">
          <Label htmlFor="placa-search">Placa</Label>
          <Input
            id="placa-search"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ex: ABC1D23 ou ABC"
            autoComplete="off"
          />
        </div>
        <Button type="submit">Buscar</Button>
      </form>

      {isLoading && <p aria-live="polite" className="text-muted">Buscando...</p>}

      {showEmpty && (
        <p role="status" className="rounded-md border border-warning/30 bg-warning/10 px-3 py-2 text-sm text-warning">
          {MSG_009}
        </p>
      )}

      {!isLoading && data.length > 0 && (
        <div className="space-y-2.5">
          {data.map((c) => (
            <div
              key={c.id}
              onClick={() => navigate(`/checklists/${c.id}`)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") navigate(`/checklists/${c.id}`);
              }}
              role="button"
              tabIndex={0}
              aria-label={`Checklist ${c.id} — ${c.placa}`}
              className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md cursor-pointer transition"
            >
              <div className="flex items-center gap-4 min-w-0">
                <StatusIcon isLocked={c.is_locked} status={c.status} />
                <div className="min-w-0">
                  <div className="font-semibold text-gray-800 truncate">
                    {c.placa}
                  </div>
                  <div className="text-xs text-gray-400">
                    Nº <span>{c.id}</span> · {c.unidade} · {formatDate(c.created_at)}
                  </div>
                </div>
              </div>
              <div className="shrink-0 ml-3">
                <StatusBadge status={c.status} isLocked={c.is_locked} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
