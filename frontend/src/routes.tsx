import { Routes, Route, Navigate, Link } from "react-router-dom";
import LoginForm from "./features/auth/LoginForm";
import RegisterForm from "./features/auth/RegisterForm";
import ChecklistForm from "./features/checklist/ChecklistForm";
import ChecklistList from "./features/checklist/ChecklistList";
import ChecklistView from "./features/checklist/ChecklistView";
import ProtectedRoute from "./components/ProtectedRoute";
import RequireRole from "./components/RequireRole";

function Dashboard() {
  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-2xl font-bold">CTRVE</h1>
      <p className="mb-6 text-muted">Checklist de Transporte de Veículos</p>
      <div className="flex gap-3">
        <Link to="/checklists/new" className="inline-flex h-9 items-center rounded-md bg-primary px-4 text-sm font-medium text-white hover:bg-primary-dark">
          Novo Checklist
        </Link>
        <Link to="/checklists" className="inline-flex h-9 items-center rounded-md border border-border px-4 text-sm font-medium hover:bg-surface">
          Buscar por Placa
        </Link>
      </div>
    </div>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/register"
        element={
          <ProtectedRoute>
            <RequireRole role="responsavel">
              <RegisterForm />
            </RequireRole>
          </ProtectedRoute>
        }
      />
      <Route
        path="/checklists"
        element={
          <ProtectedRoute>
            <ChecklistList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/checklists/new"
        element={
          <ProtectedRoute>
            <RequireRole role="responsavel">
              <ChecklistForm />
            </RequireRole>
          </ProtectedRoute>
        }
      />
      <Route
        path="/checklists/:id"
        element={
          <ProtectedRoute>
            <ChecklistView />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
