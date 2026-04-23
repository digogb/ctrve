import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";

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

const STATUS_LABELS: Record<ChecklistResponse["status"], string> = {
  entregue: "Entregue",
  devolvido: "Devolvido",
};

function statusLabel(status: ChecklistResponse["status"]): string {
  return STATUS_LABELS[status] ?? status;
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
    <div className="checklist-list">
      <h1>Buscar Checklist</h1>

      <form onSubmit={handleSubmit} className="search-form">
        <label htmlFor="placa-search">Placa</label>
        <input
          id="placa-search"
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ex: ABC1D23 ou ABC"
          autoComplete="off"
        />
        <button type="submit">Buscar</button>
      </form>

      {isLoading && <p aria-live="polite">Buscando...</p>}

      {showEmpty && (
        <p role="status">
          {MSG_009}
        </p>
      )}

      {!isLoading && data.length > 0 && (
        <table className="checklist-table">
          <thead>
            <tr>
              <th>Nº de Controle</th>
              <th>Placa</th>
              <th>Data de Registro</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((c) => (
              <tr
                key={c.id}
                onClick={() => navigate(`/checklists/${c.id}`)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") navigate(`/checklists/${c.id}`);
                }}
                style={{ cursor: "pointer" }}
                role="button"
                tabIndex={0}
                aria-label={`Checklist ${c.id} — ${c.placa}`}
              >
                <td>{c.id}</td>
                <td>{c.placa}</td>
                <td>{formatDate(c.created_at)}</td>
                <td>{statusLabel(c.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
