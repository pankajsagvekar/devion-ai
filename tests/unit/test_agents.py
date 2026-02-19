import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
from app.state import AgentState, TestResult, BugMetadata


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def sample_state():
    return AgentState(
        repository_url="https://github.com/org/repo.git",
        team_name="DevionCrew",
        leader_name="Pankaj Sagvekar",
        github_token="gho_mock_token_123",
        branch_name="DEVIONCREW_PANKAJ_SAGVEKAR_AI_FIX",
        start_time=time.time() - 120.0
    )

@pytest.fixture
def state_with_failure(sample_state):
    sample_state.current_test_results = TestResult(
        total_failures=1,
        output="F tests/test_math.py:5: AssertionError: 2 != 4",
        failures=[BugMetadata(
            file_name="tests/test_math.py",
            line_number=5,
            error_message="AssertionError: 2 != 4",
            bug_type="LOGIC"
        )]
    )
    return sample_state


# ─────────────────────────────────────────────────────────────
# Orchestrator Agent
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_orchestrator_increments_iteration(sample_state):
    from app.agents.orchestrator import orchestrator_agent
    result = await orchestrator_agent(sample_state)
    assert result.iteration == 1

@pytest.mark.asyncio
async def test_orchestrator_keeps_pending_status(sample_state):
    from app.agents.orchestrator import orchestrator_agent
    result = await orchestrator_agent(sample_state)
    assert result.final_status == "PENDING"

@pytest.mark.asyncio
async def test_orchestrator_preserves_passed_status(sample_state):
    from app.agents.orchestrator import orchestrator_agent
    sample_state.final_status = "PASSED"
    result = await orchestrator_agent(sample_state)
    assert result.final_status == "PASSED"


# ─────────────────────────────────────────────────────────────
# Analyzer Agent
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyzer_parses_logic_error(sample_state):
    from app.agents.analyzer import analyzer_agent
    sample_state.current_test_results = TestResult(
        total_failures=1,
        output="F tests/test_math.py:10: AssertionError: 0 != 1"
    )
    result = await analyzer_agent(sample_state)
    assert len(result.current_test_results.failures) == 1
    bug = result.current_test_results.failures[0]
    assert bug.line_number == 10
    assert bug.file_name == "tests/test_math.py"
    assert bug.bug_type == "LOGIC"

@pytest.mark.asyncio
async def test_analyzer_detects_import_error(sample_state):
    from app.agents.analyzer import analyzer_agent
    sample_state.current_test_results = TestResult(
        total_failures=1,
        output="F app/core.py:3: ImportError: cannot import 'foo'"
    )
    result = await analyzer_agent(sample_state)
    assert result.current_test_results.failures[0].bug_type == "IMPORT"

@pytest.mark.asyncio
async def test_analyzer_detects_type_error(sample_state):
    from app.agents.analyzer import analyzer_agent
    sample_state.current_test_results = TestResult(
        total_failures=1,
        output="F app/utils.py:7: TypeError: unsupported operand type"
    )
    result = await analyzer_agent(sample_state)
    assert result.current_test_results.failures[0].bug_type == "TYPE_ERROR"

@pytest.mark.asyncio
async def test_analyzer_skips_when_no_test_results(sample_state):
    from app.agents.analyzer import analyzer_agent
    result = await analyzer_agent(sample_state)
    assert result.current_test_results is None


# ─────────────────────────────────────────────────────────────
# Fix Generator Agent (Gemini AI-powered)
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.config.GEMINI_API_KEY", None)
async def test_fix_generator_skips_without_api_key(state_with_failure):
    from app.agents.fix_generator import fix_generator_agent
    result = await fix_generator_agent(state_with_failure)
    assert len(result.fixes_applied) == 0

@pytest.mark.asyncio
@patch("app.config.GEMINI_API_KEY", "mock_gemini_key")
@patch("os.path.exists", return_value=False)
async def test_fix_generator_skips_missing_file(mock_exists, state_with_failure):
    state_with_failure.repo_path = "/tmp/nonexistent"
    from app.agents.fix_generator import fix_generator_agent
    result = await fix_generator_agent(state_with_failure)
    assert len(result.fixes_applied) == 0

@pytest.mark.asyncio
@patch("app.config.GEMINI_API_KEY", "mock_key")
@patch("os.path.exists", return_value=True)
@patch("builtins.open", mock_open(read_data="def add(a, b): return a - b\n"))
@patch("google.generativeai.GenerativeModel")
async def test_fix_generator_writes_ai_fix(mock_model_class, mock_exists, state_with_failure):
    state_with_failure.repo_path = "/tmp/repo"
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = (
        "```python\ndef add(a, b): return a + b\n```"
    )
    mock_model_class.return_value = mock_model
    from app.agents.fix_generator import fix_generator_agent
    result = await fix_generator_agent(state_with_failure)
    assert len(result.fixes_applied) == 1
    assert "tests/test_math.py" in result.fixes_applied[0]

@pytest.mark.asyncio
async def test_fix_generator_skips_when_no_failures(sample_state):
    from app.agents.fix_generator import fix_generator_agent
    result = await fix_generator_agent(sample_state)
    assert len(result.fixes_applied) == 0


# ─────────────────────────────────────────────────────────────
# Git Agent (token-authenticated)
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.git_service.GitService.commit_and_push")
async def test_git_agent_increments_commit_count(mock_push, state_with_failure):
    state_with_failure.fixes_applied = ["AI Fix applied to tests/test_math.py"]
    state_with_failure.repo_path = "/tmp/repo"
    from app.agents.git_agent import git_agent
    result = await git_agent(state_with_failure)
    assert result.commit_count == 1

@pytest.mark.asyncio
@patch("app.services.git_service.GitService.commit_and_push")
async def test_git_agent_passes_github_token(mock_push, state_with_failure):
    state_with_failure.fixes_applied = ["fix"]
    state_with_failure.repo_path = "/tmp/repo"
    from app.agents.git_agent import git_agent
    await git_agent(state_with_failure)
    # 4th positional arg must be the github_token
    assert mock_push.call_args[0][3] == "gho_mock_token_123"

@pytest.mark.asyncio
async def test_git_agent_skips_when_no_fixes(sample_state):
    from app.agents.git_agent import git_agent
    result = await git_agent(sample_state)
    assert result.commit_count == 0


# ─────────────────────────────────────────────────────────────
# Test Runner Agent
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.docker_service.DockerService.run_in_sandbox")
@patch("app.services.git_service.GitService.create_branch")
@patch("app.services.git_service.GitService.clone_repo")
async def test_test_runner_clones_with_token(mock_clone, mock_branch, mock_sandbox, sample_state):
    mock_clone.return_value = "/tmp/repo"
    mock_sandbox.return_value = "3 passed in 0.5s"
    from app.agents.test_runner import test_runner_agent
    result = await test_runner_agent(sample_state)
    mock_clone.assert_called_once()
    # 3rd arg = github_token
    assert mock_clone.call_args[0][2] == "gho_mock_token_123"
    assert result.repo_path == "/tmp/repo"

@pytest.mark.asyncio
@patch("app.services.docker_service.DockerService.run_in_sandbox")
@patch("app.services.git_service.GitService.create_branch")
@patch("app.services.git_service.GitService.clone_repo")
async def test_test_runner_detects_failures(mock_clone, mock_branch, mock_sandbox, sample_state):
    mock_clone.return_value = "/tmp/repo"
    mock_sandbox.return_value = "1 failed, 2 passed in 1.2s"
    from app.agents.test_runner import test_runner_agent
    result = await test_runner_agent(sample_state)
    assert result.current_test_results.total_failures == 1

@pytest.mark.asyncio
@patch("app.services.docker_service.DockerService.run_in_sandbox")
@patch("app.services.git_service.GitService.create_branch")
@patch("app.services.git_service.GitService.clone_repo")
async def test_test_runner_marks_pass(mock_clone, mock_branch, mock_sandbox, sample_state):
    mock_clone.return_value = "/tmp/repo"
    mock_sandbox.return_value = "5 passed in 0.3s"
    from app.agents.test_runner import test_runner_agent
    result = await test_runner_agent(sample_state)
    assert result.current_test_results.total_failures == 0
