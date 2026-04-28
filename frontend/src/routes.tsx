import { Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./features/auth/LoginForm";
import RegisterForm from "./features/auth/RegisterForm";
import ChecklistForm from "./features/checklist/ChecklistForm";
import ChecklistList from "./features/checklist/ChecklistList";
import ChecklistView from "./features/checklist/ChecklistView";
import ProtectedRoute from "./components/ProtectedRoute";
import RequireRole from "./components/RequireRole";
import Dashboard from "./features/dashboard/Dashboard";

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
