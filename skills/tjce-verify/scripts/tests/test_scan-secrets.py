#!/usr/bin/env python3
"""Tests for scan-secrets.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scan-secrets.py"


def run_script(*dirs: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *dirs],
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "output": json.loads(result.stdout)}


def test_clean_code(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text('import os\ndb_url = os.environ["DATABASE_URL"]\n')

    result = run_script(str(src))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["total"] == 0


def test_detects_api_key(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "config.py").write_text('API_KEY = "sk_live_abcdef1234567890"\n')

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert result["output"]["summary"]["critical"] >= 1
    assert any("API key" in f["issue"] for f in result["output"]["findings"])


def test_detects_password(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "db.py").write_text('password = "super_secret_pass"\n')

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert result["output"]["summary"]["critical"] >= 1


def test_skips_env_example(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / ".env.example").write_text('API_KEY = "your_api_key_here_placeholder"\n')

    result = run_script(str(src))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"


def test_skips_node_modules(tmp_path):
    nm = tmp_path / "node_modules" / "some-pkg"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text('const token = "abcdefghijklmnopqrstuvwxyz1234567890"\n')

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"


def test_detects_private_key(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "cert.py").write_text('key = """-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----"""\n')

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert any("Private key" in f["issue"] for f in result["output"]["findings"])


def test_nonexistent_directory(tmp_path):
    result = run_script(str(tmp_path / "nonexistent"))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
    assert result["output"]["summary"]["total"] == 0
