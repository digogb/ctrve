import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";

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

function statusVariant(status: ChecklistResponse["status"]): "default" | "secondary" {
  return status === "devolvido" ? "secondary" : "default";
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
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nº</TableHead>
                <TableHead>Placa</TableHead>
                <TableHead>Data de Registro</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((c) => (
                <TableRow
                  key={c.id}
                  onClick={() => navigate(`/checklists/${c.id}`)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") navigate(`/checklists/${c.id}`);
                  }}
                  className="cursor-pointer"
                  role="button"
                  tabIndex={0}
                  aria-label={`Checklist ${c.id} — ${c.placa}`}
                >
                  <TableCell className="font-medium">{c.id}</TableCell>
                  <TableCell>{c.placa}</TableCell>
                  <TableCell>{formatDate(c.created_at)}</TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(c.status)}>{statusLabel(c.status)}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
