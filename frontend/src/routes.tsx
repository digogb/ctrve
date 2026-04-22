import { Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./features/auth/LoginForm";
import ProtectedRoute from "./components/ProtectedRoute";

function Dashboard() {
  return <div>Dashboard — em desenvolvimento</div>;
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
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
