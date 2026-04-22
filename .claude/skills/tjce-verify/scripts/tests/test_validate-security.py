#!/usr/bin/env python3
"""Tests for validate-security.py"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "validate-security.py"


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
    (src / "app.py").write_text(
        'cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))\n'
    )

    result = run_script(str(src))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"


def test_detects_fstring_sql_injection(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "db.py").write_text(
        'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")\n'
    )

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert result["output"]["status"] == "fail"
    assert any("SQL injection" in f["issue"] for f in result["output"]["findings"])


def test_detects_wildcard_cors(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "config.py").write_text('CORS_ORIGIN = "*"\n')

    # CORS check matches on the pattern, let's use a more direct match
    (src / "settings.json").write_text('{"Access-Control-Allow-Origin": "*"}\n')

    result = run_script(str(src))
    assert result["output"]["summary"]["high"] >= 1
    assert any("CORS" in f["issue"] for f in result["output"]["findings"])


def test_detects_eval(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "handler.py").write_text('result = eval(user_input)\n')

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert any("eval/exec" in f["issue"] for f in result["output"]["findings"])


def test_detects_hardcoded_jwt(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "auth.py").write_text('JWT_SECRET = "my-super-secret-jwt-key"\n')

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert any("JWT" in f["issue"] for f in result["output"]["findings"])


def test_detects_ssl_verify_false(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "client.py").write_text('requests.get(url, verify=False)\n')

    result = run_script(str(src))
    assert result["output"]["summary"]["high"] >= 1
    assert any("SSL" in f["issue"] for f in result["output"]["findings"])


def test_detects_template_literal_sql_js(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "query.ts").write_text(
        'const result = db.query(`SELECT * FROM users WHERE id = ${userId}`);\n'
    )

    result = run_script(str(src))
    assert result["returncode"] == 1
    assert any("SQL injection" in f["issue"] for f in result["output"]["findings"])


def test_skips_migrations(tmp_path):
    mig = tmp_path / "migrations"
    mig.mkdir()
    (mig / "001.py").write_text('cursor.execute(f"ALTER TABLE {table}")\n')

    result = run_script(str(tmp_path))
    assert result["returncode"] == 0
    assert result["output"]["status"] == "pass"
