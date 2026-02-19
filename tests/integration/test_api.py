import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
@patch("app.graph.create_graph")
async def test_run_agent_endpoint(mock_create_graph, client):
    # Mock the graph execution
    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = {
        "results_json": {
            "final_status": "PASSED",
            "score_calculation": {"final_score": 110}
        }
    }
    mock_create_graph.return_value = mock_graph
    
    payload = {
        "repository_url": "https://github.com/test/repo",
        "team_name": "TEAM_A",
        "leader_name": "LEADER_A"
    }
    
    response = client.post("/run-agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "PASSED"
    assert data["score_calculation"]["final_score"] == 110
