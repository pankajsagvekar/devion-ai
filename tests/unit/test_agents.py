import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from app.state import AgentState, TestResult, BugMetadata
from app.agents.orchestrator import orchestrator_agent
from app.agents.analyzer import analyzer_agent
from app.agents.fix_generator import fix_generator_agent
from app.agents.git_agent import git_agent
from app.agents.test_runner import test_runner_agent

@pytest.mark.asyncio
async def test_orchestrator_agent(sample_agent_state):
    state = await orchestrator_agent(sample_agent_state)
    assert state.iteration == 1
    assert state.final_status == "PENDING"

@pytest.mark.asyncio
async def test_analyzer_agent(sample_agent_state):
    sample_agent_state.current_test_results = TestResult(
        total_failures=1,
        output="F tests/test_math.py:5: AssertionError: 2 != 4"
    )
    state = await analyzer_agent(sample_agent_state)
    assert len(state.current_test_results.failures) == 1
    failure = state.current_test_results.failures[0]
    assert failure.file_name == "tests/test_math.py"
    assert failure.line_number == 5
    assert failure.bug_type == "LOGIC"

@pytest.mark.asyncio
async def test_fix_generator_agent(sample_agent_state):
    sample_agent_state.current_test_results = TestResult(
        total_failures=1,
        failures=[BugMetadata(file_name="test.py", line_number=1, error_message="msg", bug_type="LOGIC")],
        output=""
    )
    state = await fix_generator_agent(sample_agent_state)
    assert len(state.fixes_applied) == 1
    assert "test.py" in state.fixes_applied[0]

@pytest.mark.asyncio
@patch("app.services.git_service.GitService.commit_and_push")
async def test_git_agent(mock_push, sample_agent_state):
    sample_agent_state.fixes_applied = ["Fix description"]
    sample_agent_state.repo_path = "/tmp/repo"
    state = await git_agent(sample_agent_state)
    assert state.commit_count == 1
    mock_push.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.docker_service.DockerService.run_in_sandbox")
@patch("app.services.git_service.GitService.clone_repo")
@patch("app.services.git_service.GitService.create_branch")
async def test_test_runner_agent(mock_branch, mock_clone, mock_sandbox, sample_agent_state):
    mock_clone.return_value = "/tmp/repo"
    mock_sandbox.return_value = "PASSED in 0.01s"
    state = await test_runner_agent(sample_agent_state)
    assert state.repo_path == "/tmp/repo"
    assert state.current_test_results.total_failures == 0
    assert "PASSED" in state.current_test_results.output
