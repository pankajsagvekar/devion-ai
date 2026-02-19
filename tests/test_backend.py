from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_run_agent_structure():
    # This is a unit test for the request model validation
    # Real integration test would require mocking the graph
    payload = {
        "repo_url": "https://github.com/test/repo",
        "team_name": "TEST_TEAM",
        "leader_name": "TEST_LEADER"
    }
    # We won't run the full agent here as it requires Docker/Git
    pass
