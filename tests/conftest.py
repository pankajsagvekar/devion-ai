import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.state import AgentState

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_agent_state():
    return AgentState(
        repository_url="https://github.com/mock/repo",
        team_name="MOCK_TEAM",
        leader_name="MOCK_LEADER",
        branch_name="MOCK_TEAM_MOCK_LEADER_AI_FIX",
        start_time=1700000000.0
    )
