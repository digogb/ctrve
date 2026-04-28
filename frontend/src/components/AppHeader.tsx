import { Link } from "react-router-dom";
import { useAuthContext } from "../features/auth/AuthContext";

export default function AppHeader() {
  const { user, logout } = useAuthContext();

  const initials =
    user?.full_name
      .split(" ")
      .filter((n) => n)
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "??";

  const roleLabel = user?.role === "responsavel" ? "Responsável" : "Motorista";

  return (
    <header className="sticky top-0 z-50 shadow-md bg-gradient-to-br from-[#003366] to-[#004080] text-white">
      <div className="mx-auto max-w-5xl px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <div className="w-8 h-8 rounded bg-white/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="size-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <div className="font-bold text-base leading-none">CTRVE</div>
              <div className="text-xs text-blue-200 leading-none mt-0.5 hidden sm:block">
                Checklist de Transporte de Veículos
              </div>
            </div>
          </Link>
          <nav className="hidden sm:flex items-center gap-1 ml-2">
            <Link
              to="/"
              className="text-sm text-blue-100 hover:text-white hover:bg-white/10 px-3 py-1.5 rounded-lg transition"
            >
              Início
            </Link>
            <Link
              to="/checklists"
              className="text-sm text-blue-100 hover:text-white hover:bg-white/10 px-3 py-1.5 rounded-lg transition"
            >
              Buscar
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-white/10 rounded-full px-3 py-1.5">
            <div className="w-6 h-6 rounded-full bg-white/30 flex items-center justify-center text-xs font-bold">
              {initials}
            </div>
            <div className="text-sm">
              <span className="font-medium">{user?.full_name}</span>
              <span className="text-blue-200 ml-1.5 text-xs">{roleLabel}</span>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="text-sm text-blue-200 hover:text-white transition"
          >
            Sair
          </button>
        </div>
      </div>
    </header>
  );
}
