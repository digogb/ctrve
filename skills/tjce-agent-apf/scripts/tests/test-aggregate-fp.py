"""Unit tests for aggregate-fp.py"""

import importlib.util
import pytest
from pathlib import Path

_script_path = Path(__file__).parent.parent / "aggregate-fp.py"
_spec = importlib.util.spec_from_file_location("aggregate_fp", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

aggregate = _mod.aggregate
render_markdown = _mod.render_markdown


def test_empty_functions():
    r = aggregate([], tdi=35)
    assert r["pf_brutos"] == 0
    assert r["vaf"] == 1.0
    assert r["pf_ajustado"] == 0.0
    assert r["total_functions"] == 0


def test_basic_aggregation():
    functions = [
        {"id": "FD-001", "type": "ALI", "pf": 7, "complexity": "Baixa"},
        {"id": "FD-002", "type": "ALI", "pf": 10, "complexity": "Media"},
        {"id": "FT-001", "type": "EE", "pf": 4, "complexity": "Media"},
    ]
    r = aggregate(functions, tdi=35)
    assert r["pf_brutos"] == 21
    assert r["vaf"] == 1.0
    assert r["pf_ajustado"] == 21.0
    assert r["total_functions"] == 3


def test_vaf_low_boundary():
    r = aggregate([{"type": "ALI", "pf": 10}], tdi=0)
    assert r["vaf"] == 0.65
    assert r["pf_ajustado"] == 6.5


def test_vaf_high_boundary():
    r = aggregate([{"type": "ALI", "pf": 10}], tdi=70)
    assert r["vaf"] == 1.35
    assert r["pf_ajustado"] == 13.5


def test_invalid_tdi_rejected():
    with pytest.raises(ValueError, match="TDI"):
        aggregate([], tdi=-1)
    with pytest.raises(ValueError, match="TDI"):
        aggregate([], tdi=71)


def test_unknown_type_rejected():
    with pytest.raises(ValueError, match="unknown type"):
        aggregate([{"id": "X", "type": "XX", "pf": 5}], tdi=35)


def test_distribution_percentages():
    functions = [
        {"type": "ALI", "pf": 10},
        {"type": "EE", "pf": 30},
        {"type": "SE", "pf": 10},
    ]
    r = aggregate(functions, tdi=35)
    assert r["pf_brutos"] == 50
    by_type = {d["type"]: d for d in r["distribution"]}
    assert by_type["ALI"]["pct"] == 20.0
    assert by_type["EE"]["pct"] == 60.0
    assert by_type["SE"]["pct"] == 20.0
    assert by_type["AIE"]["count"] == 0
    assert by_type["AIE"]["pf"] == 0


def test_render_markdown_contains_headers():
    r = aggregate([{"type": "ALI", "pf": 7}], tdi=35)
    md = render_markdown(r)
    assert "PF Brutos" in md
    assert "**PF Ajustado**" in md
    assert "Distribuicao por Tipo" in md
    assert "| ALI |" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
