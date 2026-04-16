"""Unit tests for parse-coverage.py"""

import importlib.util
import sys
from pathlib import Path

# Import module with hyphenated filename
_script_path = Path(__file__).parent.parent / "parse-coverage.py"
_spec = importlib.util.spec_from_file_location("parse_coverage", _script_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_pytest_cov = _mod.parse_pytest_cov
parse_jest_coverage = _mod.parse_jest_coverage
parse_coverage = _mod.parse_coverage


# --- parse_pytest_cov ---


def test_pytest_cov_basic():
    text = """\
Name                      Stmts   Miss  Cover   Missing
--------------------------------------------------------
backend/app/main.py          45      3    93%   12-14
backend/app/utils.py         30     10    67%   5-8, 20-25
--------------------------------------------------------
TOTAL                        75     13    83%
"""
    result = parse_pytest_cov(text)
    assert result is not None
    assert result["tool"] == "pytest-cov"
    assert result["total_coverage"] == 83
    assert result["total_statements"] == 75
    assert result["total_missing"] == 13
    assert len(result["files"]) == 2
    assert result["files"][0]["file"] == "backend/app/main.py"
    assert result["files"][0]["coverage"] == 93
    assert result["files"][0]["missing_lines"] == "12-14"
    assert result["files"][1]["coverage"] == 67


def test_pytest_cov_no_missing_column():
    text = """\
Name              Stmts   Miss  Cover
--------------------------------------
app/models.py        20      0   100%
"""
    result = parse_pytest_cov(text)
    assert result is not None
    assert result["files"][0]["coverage"] == 100
    assert result["files"][0]["missing_lines"] == ""


def test_pytest_cov_no_total_line():
    text = """\
backend/app/main.py    50     10    80%   1-10
backend/app/api.py     50      5    90%   45-49
"""
    result = parse_pytest_cov(text)
    assert result is not None
    # Should calculate from individual files: (100 - 15) / 100 * 100 = 85
    assert result["total_coverage"] == 85
    assert result["total_statements"] == 100
    assert result["total_missing"] == 15


def test_pytest_cov_single_file():
    text = "app/main.py    10      0   100%\n"
    result = parse_pytest_cov(text)
    assert result is not None
    assert result["total_coverage"] == 100
    assert len(result["files"]) == 1


def test_pytest_cov_no_match():
    result = parse_pytest_cov("no coverage data here")
    assert result is None


def test_pytest_cov_zero_statements():
    text = "app/empty.py    0      0     0%\n"
    result = parse_pytest_cov(text)
    assert result is not None
    assert result["total_coverage"] == 0


# --- parse_jest_coverage ---


def test_jest_coverage_basic():
    text = """\
----------|---------|----------|---------|---------|-------------------
File      | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
----------|---------|----------|---------|---------|-------------------
All files |   85.71 |      100 |   66.67 |   85.71 |
 main.ts  |   85.71 |      100 |   66.67 |   85.71 | 15-20
 utils.ts |   90.00 |       80 |  100.00 |   90.00 | 42
----------|---------|----------|---------|---------|-------------------
"""
    result = parse_jest_coverage(text)
    assert result is not None
    assert result["tool"] == "jest"
    assert result["total_coverage"] == 85.71
    assert len(result["files"]) == 2
    assert result["files"][0]["file"] == "main.ts"
    assert result["files"][0]["statements"] == 85.71
    assert result["files"][0]["branches"] == 100.0
    assert result["files"][0]["uncovered_lines"] == "15-20"
    assert result["files"][1]["file"] == "utils.ts"


def test_jest_coverage_no_uncovered():
    text = """\
 index.ts |     100 |      100 |     100 |     100 |
All files |     100 |      100 |     100 |     100 |
"""
    result = parse_jest_coverage(text)
    assert result is not None
    assert result["total_coverage"] == 100.0
    assert len(result["files"]) == 1
    assert result["files"][0]["file"] == "index.ts"


def test_jest_coverage_no_all_files_line():
    text = " app.ts |   70.00 |   50.00 |   80.00 |   75.00 | 10-15\n"
    result = parse_jest_coverage(text)
    assert result is not None
    # Should average lines % from individual files
    assert result["total_coverage"] == 75.0


def test_jest_coverage_no_match():
    result = parse_jest_coverage("no jest data here")
    assert result is None


# --- parse_coverage (auto-detection) ---


def test_parse_coverage_detects_pytest():
    text = "app/main.py    50     5    90%   1-5\nTOTAL    50     5    90%\n"
    result = parse_coverage(text)
    assert result is not None
    assert result["tool"] == "pytest-cov"


def test_parse_coverage_detects_jest():
    text = """\
----------|---------|----------|---------|---------|-------------------
File      | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
----------|---------|----------|---------|---------|-------------------
All files |   90.00 |      100 |   80.00 |   90.00 |
 app.ts   |   90.00 |      100 |   80.00 |   90.00 | 5
----------|---------|----------|---------|---------|-------------------
"""
    result = parse_coverage(text)
    assert result is not None
    assert result["tool"] == "jest"


def test_parse_coverage_no_match():
    result = parse_coverage("nothing parseable")
    assert result is None


# --- threshold and below_threshold (integration-style) ---


def test_pytest_files_below_threshold():
    text = """\
app/good.py    100      5    95%   1-5
app/bad.py      50     20    60%   10-29
TOTAL          150     25    83%
"""
    result = parse_coverage(text)
    assert result is not None
    assert result["total_coverage"] == 83
    # Verify we can identify files below 80%
    below = [f for f in result["files"] if f["coverage"] < 80]
    assert len(below) == 1
    assert below[0]["file"] == "app/bad.py"


def test_jest_files_below_threshold():
    text = """\
 good.ts  |   95.00 |      100 |  100.00 |   95.00 |
 bad.ts   |   50.00 |       30 |   40.00 |   50.00 | 1-25
All files |   85.00 |      100 |   80.00 |   85.00 |
"""
    result = parse_coverage(text)
    assert result is not None
    below = [f for f in result["files"] if f["lines"] < 80]
    assert len(below) == 1
    assert below[0]["file"] == "bad.ts"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
