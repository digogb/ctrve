"""Unit tests for extract-screens.py"""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

_script_path = Path(__file__).parent.parent / "extract-screens.py"
_spec = importlib.util.spec_from_file_location("extract_screens", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

scan_file = _mod.scan_file
scan_directory = _mod.scan_directory
extract_nextjs_routes = _mod.extract_nextjs_routes
build_inventory = _mod.build_inventory


@pytest.fixture
def tmp_frontend(tmp_path):
    """Create a minimal frontend structure."""
    src = tmp_path / "src"
    src.mkdir()
    return src


def _write_tsx(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- scan_file ---

def test_scan_file_detects_component_and_labels(tmp_frontend):
    tsx = tmp_frontend / "LoginPage.tsx"
    _write_tsx(tsx, """\
export default function LoginPage() {
  return (
    <form>
      <label>Usuario</label>
      <input placeholder="Digite seu usuario" />
      <Button>Entrar</Button>
    </form>
  );
}
""")
    result = scan_file(tsx)
    assert result is not None
    assert "LoginPage" in result["components"]
    assert "Usuario" in result["labels"]
    assert "Digite seu usuario" in result["placeholders"]
    assert "Entrar" in result["buttons"]


def test_scan_file_skips_utility(tmp_frontend):
    ts = tmp_frontend / "utils.ts"
    _write_tsx(ts, """\
export function formatDate(d: Date): string {
  return d.toISOString();
}
""")
    # No UI elements → should return None
    assert scan_file(ts) is None


def test_scan_file_extracts_routes(tmp_frontend):
    tsx = tmp_frontend / "Router.tsx"
    _write_tsx(tsx, """\
export function AppRouter() {
  return (
    <Routes>
      <Route path="/processos" element={<ProcessoList />} />
      <Route path="/processos/:id" element={<ProcessoDetail />} />
    </Routes>
  );
}
""")
    result = scan_file(tsx)
    assert result is not None
    assert "/processos" in result["routes"]
    assert "/processos/:id" in result["routes"]


def test_scan_file_extracts_headings(tmp_frontend):
    tsx = tmp_frontend / "Dashboard.tsx"
    _write_tsx(tsx, """\
export function Dashboard() {
  return <h1>Painel de Controle</h1>;
}
""")
    result = scan_file(tsx)
    assert result is not None
    assert "Painel de Controle" in result["headings"]


def test_scan_file_extracts_help_text(tmp_frontend):
    tsx = tmp_frontend / "Form.tsx"
    _write_tsx(tsx, """\
export function ProcessForm() {
  return <Input label="CPF" helpText="Informe os 11 digitos" />;
}
""")
    result = scan_file(tsx)
    assert result is not None
    assert "Informe os 11 digitos" in result["help_texts"]
    assert "CPF" in result["labels"]


# --- scan_directory ---

def test_scan_directory_skips_node_modules(tmp_frontend):
    nm = tmp_frontend / "node_modules" / "pkg"
    _write_tsx(nm / "Component.tsx", """\
export function Component() { return <Button>Click</Button>; }
""")
    results = scan_directory(tmp_frontend)
    assert len(results) == 0


def test_scan_directory_skips_test_files(tmp_frontend):
    _write_tsx(tmp_frontend / "Login.test.tsx", """\
export function Login() { return <label>Test</label>; }
""")
    results = scan_directory(tmp_frontend)
    assert len(results) == 0


def test_scan_directory_collects_screens(tmp_frontend):
    _write_tsx(tmp_frontend / "PageA.tsx", """\
export function PageA() { return <label>Campo A</label>; }
""")
    _write_tsx(tmp_frontend / "PageB.tsx", """\
export function PageB() { return <Button>Salvar</Button>; }
""")
    results = scan_directory(tmp_frontend)
    assert len(results) == 2


# --- extract_nextjs_routes ---

def test_nextjs_pages_routes(tmp_path):
    pages = tmp_path / "pages"
    _write_tsx(pages / "index.tsx", "export default function Home() {}")
    _write_tsx(pages / "processos" / "index.tsx", "export default function P() {}")
    _write_tsx(pages / "processos" / "[id].tsx", "export default function D() {}")

    routes = extract_nextjs_routes(tmp_path)
    paths = [r["route"] for r in routes]
    assert "/" in paths
    assert "/processos" in paths
    assert "/processos/:id" in paths


def test_nextjs_no_pages(tmp_path):
    assert extract_nextjs_routes(tmp_path) == []


# --- build_inventory ---

def test_build_inventory_summary(tmp_frontend):
    _write_tsx(tmp_frontend / "Login.tsx", """\
export function LoginPage() {
  return (
    <form>
      <label>Email</label>
      <label>Senha</label>
      <Button>Entrar</Button>
    </form>
  );
}
""")
    inventory = build_inventory(tmp_frontend)
    assert inventory["summary"]["total_screen_files"] == 1
    assert inventory["summary"]["total_labels"] == 2
    assert inventory["summary"]["total_buttons"] == 1
    assert inventory["summary"]["total_components"] == 1


def test_build_inventory_empty(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    inventory = build_inventory(empty)
    assert inventory["summary"]["total_screen_files"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
