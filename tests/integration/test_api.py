import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


# ─────────────────────────────────────────────────────────────
# Reusable helpers
# ─────────────────────────────────────────────────────────────

VALID_PAYLOAD = {
    "repository_url": "https://github.com/org/buggy-repo.git",
    "github_token": "gho_mock_token_123",
    "team_name": "DevionCrew",
    "team_leader": "Pankaj Sagvekar"
}

VALID_RESULTS = {
    "repository_url": "https://github.com/org/buggy-repo.git",
    "team_name": "DevionCrew",
    "leader_name": "Pankaj Sagvekar",
    "branch_name": "DEVIONCREW_PANKAJ_SAGVEKAR_AI_FIX",
    "total_failures": 1,
    "total_fixes": 1,
    "iterations_used": 1,
    "commit_count": 1,
    "final_status": "PASSED",
    "total_time_seconds": 145.0,
    "score_calculation": {
        "base_score": 100,
        "speed_bonus": 10,
        "efficiency_penalty": 0,
        "final_score": 110
    }
}


def _client():
    return TestClient(app, raise_server_exceptions=False)


def _mock_graph(results=VALID_RESULTS):
    """Helper: returns mock graph with a real async ainvoke."""
    async def fake_invoke(state):
        return {"results_json": results}

    g = MagicMock()
    g.ainvoke = fake_invoke
    return g


# ─────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────

def test_health_returns_200():
    assert _client().get("/health").status_code == 200

def test_health_returns_healthy_body():
    assert _client().get("/health").json() == {"status": "healthy"}


# ─────────────────────────────────────────────────────────────
# POST /run-agent — Validation (4 required fields)
# ─────────────────────────────────────────────────────────────

def test_run_agent_missing_repo_url():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "repository_url"}
    assert _client().post("/run-agent", json=payload).status_code == 422

def test_run_agent_missing_github_token():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "github_token"}
    assert _client().post("/run-agent", json=payload).status_code == 422

def test_run_agent_missing_team_name():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "team_name"}
    assert _client().post("/run-agent", json=payload).status_code == 422

def test_run_agent_missing_team_leader():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "team_leader"}
    assert _client().post("/run-agent", json=payload).status_code == 422

def test_run_agent_empty_body():
    r = _client().post("/run-agent", json={})
    assert r.status_code == 422
    assert len(r.json()["detail"]) >= 4


# ─────────────────────────────────────────────────────────────
# POST /run-agent — Happy Path
# ─────────────────────────────────────────────────────────────

def test_run_agent_returns_200():
    with patch("app.main.create_graph", return_value=_mock_graph()):
        r = _client().post("/run-agent", json=VALID_PAYLOAD)
    assert r.status_code == 200

def test_run_agent_returns_results_json():
    with patch("app.main.create_graph", return_value=_mock_graph()):
        r = _client().post("/run-agent", json=VALID_PAYLOAD)
    assert r.json()["final_status"] == "PASSED"
    assert r.json()["score_calculation"]["final_score"] == 110

def test_run_agent_all_result_fields_present():
    with patch("app.main.create_graph", return_value=_mock_graph()):
        data = _client().post("/run-agent", json=VALID_PAYLOAD).json()
    required = [
        "repository_url", "team_name", "leader_name", "branch_name",
        "total_failures", "total_fixes", "iterations_used", "commit_count",
        "final_status", "total_time_seconds", "score_calculation"
    ]
    for field in required:
        assert field in data, f"Missing field: {field}"

def test_run_agent_score_calculation_keys():
    with patch("app.main.create_graph", return_value=_mock_graph()):
        sc = _client().post("/run-agent", json=VALID_PAYLOAD).json()["score_calculation"]
    for key in ["base_score", "speed_bonus", "efficiency_penalty", "final_score"]:
        assert key in sc, f"Missing score key: {key}"


# ─────────────────────────────────────────────────────────────
# POST /run-agent — Branch Name Formation
# ─────────────────────────────────────────────────────────────

def test_run_agent_branch_name_from_team_name_and_leader():
    """Branch must be TEAM_NAME_TEAM_LEADER_AI_FIX (uppercased, spaces→_)."""
    captured = {}

    async def fake_invoke(state):
        captured["branch"] = state.branch_name
        return {"results_json": VALID_RESULTS}

    g = MagicMock()
    g.ainvoke = fake_invoke

    with patch("app.main.create_graph", return_value=g):
        _client().post("/run-agent", json={
            "repository_url": "https://github.com/org/repo",
            "github_token": "gho_token",
            "team_name": "Code Ninjas",
            "team_leader": "John Smith"
        })
    assert captured["branch"] == "CODE_NINJAS_JOHN_SMITH_AI_FIX"

def test_run_agent_branch_ends_with_ai_fix():
    captured = {}

    async def fake_invoke(state):
        captured["branch"] = state.branch_name
        return {"results_json": VALID_RESULTS}

    g = MagicMock()
    g.ainvoke = fake_invoke

    with patch("app.main.create_graph", return_value=g):
        _client().post("/run-agent", json=VALID_PAYLOAD)
    assert captured["branch"].endswith("_AI_FIX")

def test_run_agent_branch_has_no_spaces():
    captured = {}

    async def fake_invoke(state):
        captured["branch"] = state.branch_name
        return {"results_json": VALID_RESULTS}

    g = MagicMock()
    g.ainvoke = fake_invoke

    with patch("app.main.create_graph", return_value=g):
        _client().post("/run-agent", json={
            "repository_url": "https://github.com/org/repo",
            "github_token": "gho_token",
            "team_name": "My Team",
            "team_leader": "My Leader"
        })
    assert " " not in captured["branch"]


# ─────────────────────────────────────────────────────────────
# POST /run-agent — State Field Passing
# ─────────────────────────────────────────────────────────────

def test_run_agent_github_token_passed_to_state():
    captured = {}

    async def fake_invoke(state):
        captured["token"] = state.github_token
        return {"results_json": VALID_RESULTS}

    g = MagicMock()
    g.ainvoke = fake_invoke

    with patch("app.main.create_graph", return_value=g):
        _client().post("/run-agent", json=VALID_PAYLOAD)
    assert captured["token"] == "gho_mock_token_123"

def test_run_agent_team_name_passed_to_state():
    captured = {}

    async def fake_invoke(state):
        captured["team"] = state.team_name
        return {"results_json": VALID_RESULTS}

    g = MagicMock()
    g.ainvoke = fake_invoke

    with patch("app.main.create_graph", return_value=g):
        _client().post("/run-agent", json=VALID_PAYLOAD)
    assert captured["team"] == "DevionCrew"

def test_run_agent_team_leader_mapped_to_leader_name_in_state():
    """team_leader from request → leader_name in AgentState."""
    captured = {}

    async def fake_invoke(state):
        captured["leader"] = state.leader_name
        return {"results_json": VALID_RESULTS}

    g = MagicMock()
    g.ainvoke = fake_invoke

    with patch("app.main.create_graph", return_value=g):
        _client().post("/run-agent", json=VALID_PAYLOAD)
    assert captured["leader"] == "Pankaj Sagvekar"


# ─────────────────────────────────────────────────────────────
# GitHub OAuth
# ─────────────────────────────────────────────────────────────

def test_auth_login_redirects_to_github():
    with patch("app.main.GITHUB_CLIENT_ID", "mock_id"):
        client = TestClient(app, raise_server_exceptions=False, allow_redirects=False)
        r = client.get("/auth/login")
    assert r.status_code in (302, 307)
    assert "github.com/login/oauth/authorize" in r.headers.get("location", "")

def test_auth_callback_no_code_returns_400():
    r = _client().get("/auth/callback")
    assert r.status_code == 400
    assert "No code" in r.json()["detail"]
