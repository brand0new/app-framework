"""Tests for the A2A Agent Card."""

import json
from pathlib import Path


def test_agent_card_is_valid_json():
    card_path = Path("appygentic/a2a/agent_card.json")
    assert card_path.exists()
    card = json.loads(card_path.read_text())
    assert "name" in card
    assert "version" in card
    assert "skills" in card


def test_agent_card_has_required_fields():
    card_path = Path("appygentic/a2a/agent_card.json")
    card = json.loads(card_path.read_text())

    assert card["name"] == "Appygentic PM Agent"
    assert card["version"] == "2.0.0"
    assert card["capabilities"]["streaming"] is True
    assert len(card["skills"]) >= 4


def test_agent_card_skills_have_required_fields():
    card_path = Path("appygentic/a2a/agent_card.json")
    card = json.loads(card_path.read_text())

    for skill in card["skills"]:
        assert "id" in skill
        assert "name" in skill
        assert "description" in skill


def test_agent_card_has_authentication():
    card_path = Path("appygentic/a2a/agent_card.json")
    card = json.loads(card_path.read_text())

    assert len(card["authentication"]) >= 1
    auth_types = [a["type"] for a in card["authentication"]]
    assert "OAuth2" in auth_types
    assert "ApiKey" in auth_types
