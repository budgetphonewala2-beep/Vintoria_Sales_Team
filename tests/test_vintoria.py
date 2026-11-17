"""Vintoria personalisation: the preset profile, India as a target market, AI and automation as services,
and the catalog the skills cite."""

import json
import re
from pathlib import Path

import pytest

import intent_scan
import query_library
import seller_profile

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "skills" / "vintoria-sales" / "references"


@pytest.fixture(autouse=True)
def here(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)


def test_preset_fills_only_catalog_facts():
    with pytest.raises(SystemExit):
        seller_profile.main(["init", "--preset", "vintoria"])
    prof = seller_profile.load()
    assert prof["seller"]["company"] == "Vintoria"
    assert {"ai", "automation", "web", "ecommerce"} <= set(prof["offer"]["services"])
    assert prof["targets"]["countries"] == ["IN", "US", "UK", "AU"] and prof["targets"]["exclude_countries"] == []
    # nothing the user hasn't told us: identity, prices and proof stay empty until the interview
    assert prof["seller"]["name"] == "" and prof["offer"]["deal_size"]["typical"] is None and prof["proof"]["case_studies"] == []
    missing = seller_profile.check(prof)["missing_required"]
    assert {"seller.name", "seller.email", "proof.case_studies", "offer.deal_size"} <= set(missing)
    assert "offer.services" not in missing and "targets.countries" not in missing


def test_india_is_a_target_market():
    assert query_library.COUNTRIES["IN"]["tz"] == "Asia/Kolkata" and "Pune" in query_library.COUNTRIES["IN"]["cities"]
    assert query_library.ALIASES["INDIA"] == "IN"


def test_ai_and_automation_are_huntable():
    for table in (query_library.TERMS, query_library.NEEDS, query_library.HINGLISH, query_library.REDDIT,
                  query_library.HN, query_library.MAPS):
        assert "ai" in table and "automation" in table
    r = intent_scan.score_text("Looking for someone to build an AI chatbot for our clinic website, any recommendations?")
    assert r["keep"] and "ai" in r["services"]
    r = intent_scan.score_text("Need help to automate our lead follow-up with Zapier and HubSpot, who can do this?")
    assert r["keep"] and "automation" in r["services"]


def test_catalog_has_270_services_and_skills_cite_real_ids():
    ids = {}
    for f in sorted(REFS.glob("services-*.md")):
        for m in re.finditer(r"^\| (\d{3}) \| ([^|]+?) \|", f.read_text(encoding="utf-8"), re.M):
            ids[m.group(1)] = m.group(2).strip()
    assert len(ids) == 270 and min(ids) == "001" and max(ids) == "270"
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        for sid, name in re.findall(r"`(\d{3}) ([A-Z][\w/&,.' -]+?)`", skill.read_text(encoding="utf-8")):
            assert ids.get(sid) == name, f"{skill.parent.name}: `{sid} {name}` is not the catalog name ({ids.get(sid)})"


def test_catalog_json_matches_the_reference_files():
    data = json.loads((ROOT / "docs" / "vintoria" / "service-catalog.json").read_text(encoding="utf-8"))
    assert len(data) == 12 and sum(len(v) for v in data.values()) == 270
