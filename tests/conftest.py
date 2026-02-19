import pytest
import time
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# --- conftest.py fixtures ---
# This file provides shared fixtures for all tests
from app.state import AgentState, TestResult, BugMetadata

@pytest.fixture
def client():
    """FastAPI test client with mocked config to avoid missing env vars errors."""
    with patch("app.config.GITHUB_CLIENT_ID", "mock_client_id"), \
         patch("app.config.GITHUB_CLIENT_SECRET", "mock_secret"), \
         patch("app.config.GEMINI_API_KEY", "mock_gemini_key"), \
         patch("app.config.TEAM_NAME", "DEVIONCREW"), \
         patch("app.config.LEADER_NAME", "PANKAJ_SAGVEKAR"):
        from app.main import app
        return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def sample_state():
    """A base AgentState for unit test use."""
    return AgentState(
        repository_url="https://github.com/mock/repo",
        team_name="DEVIONCREW",
        leader_name="PANKAJ_SAGVEKAR",
        github_token="mock_github_token_123",
        branch_name="DEVIONCREW_PANKAJ_SAGVEKAR_AI_FIX",
        start_time=time.time() - 100.0
    )

@pytest.fixture
def state_with_failure(sample_state):
    """AgentState seeded with a test failure."""
    sample_state.current_test_results = TestResult(
        total_failures=1,
        output="FAILED tests/test_math.py::test_add - AssertionError: 2 != 4\nF tests/test_math.py:5: AssertionError: 2 != 4",
        failures=[
            BugMetadata(
                file_name="tests/test_math.py",
                line_number=5,
                error_message="AssertionError: 2 != 4",
                bug_type="LOGIC"
            )
        ]
    )
    return sample_state
