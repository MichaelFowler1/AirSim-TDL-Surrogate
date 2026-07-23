"""The ETL chain is the system's authority: spec text -> regex scrape ->
JSON ICD -> SQLite rules the C2 terminal decodes against. These tests pin
the scraper's parse of the real mock spec and the full chain end to end,
with no AirSim instance required."""
import json
import os
import sqlite3

import pytest
from conftest import REPO

import db_loader
import wicked_scraper


# The four J-series message types the surrogate documents supporting.
DOCUMENTED_MESSAGES = {"J0.0", "J2.2", "J3.2", "J28.2"}


def test_scraper_parses_real_spec(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spec = open(os.path.join(REPO, "mock_cmn4_spec.txt")).read()
    (tmp_path / "mock_cmn4_spec.txt").write_text(spec)

    wicked_scraper.scrape_rules()

    rules = json.load(open(tmp_path / "cmn4_interface_control.json"))
    ids = {r["id"] for r in rules}
    assert DOCUMENTED_MESSAGES <= ids, "documented J-series types must parse"
    # Link 16 J-series words are fixed-width: every parsed field carries an
    # explicit positive bit length.
    assert all(isinstance(r["bits"], int) and r["bits"] > 0 for r in rules)
    assert all(r["name"] for r in rules)


def test_scraper_skips_malformed_lines(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "mock_cmn4_spec.txt").write_text(
        "Field J0.0 | Initial Entry | 75 bits | Network Sync |\n"
        "this line is prose and must not parse\n"
        "Field J9.9 | Missing Bits | many bits | Broken |\n"
        "Field J2.2 | Air PPLI | 75 bits | Friendly Position |\n"
    )

    wicked_scraper.scrape_rules()

    rules = json.load(open(tmp_path / "cmn4_interface_control.json"))
    assert [r["id"] for r in rules] == ["J0.0", "J2.2"]


def test_spec_to_sqlite_round_trip(tmp_path, monkeypatch):
    """Full chain: spec text -> scraper -> JSON -> db_loader -> queryable rules."""
    monkeypatch.chdir(tmp_path)
    spec = open(os.path.join(REPO, "mock_cmn4_spec.txt")).read()
    (tmp_path / "mock_cmn4_spec.txt").write_text(spec)
    wicked_scraper.scrape_rules()

    # Point the loader at the tmp sandbox instead of the repo checkout.
    monkeypatch.setattr(db_loader, "JSON_INPUT",
                        str(tmp_path / "cmn4_interface_control.json"))
    monkeypatch.setattr(db_loader, "DB_PATH", str(tmp_path / "tactical.db"))
    db_loader.load_json_to_db()

    conn = sqlite3.connect(tmp_path / "tactical.db")
    rows = conn.execute(
        "SELECT id, name, bits, type FROM tactical_rules").fetchall()
    conn.close()

    by_id = {r[0]: r for r in rows}
    assert DOCUMENTED_MESSAGES <= set(by_id)
    assert by_id["J2.2"][1] == "Air PPLI"
    assert by_id["J3.2"][3] == "Surveillance"
    assert all(r[2] == 75 for r in by_id.values()), \
        "J-series words in this spec are 75-bit"


def test_loader_without_icd_is_a_noop(tmp_path, monkeypatch):
    monkeypatch.setattr(db_loader, "JSON_INPUT", str(tmp_path / "missing.json"))
    monkeypatch.setattr(db_loader, "DB_PATH", str(tmp_path / "tactical.db"))
    db_loader.load_json_to_db()
    assert not (tmp_path / "tactical.db").exists()
