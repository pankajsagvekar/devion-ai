import pytest
import time
from app.state import AgentState, TestResult


# ─────────────────────────────────────────────────────────────
# calculate_score
# ─────────────────────────────────────────────────────────────

def _base_state():
    return AgentState(
        repository_url="https://github.com/mock/repo",
        team_name="DEVIONCREW",
        leader_name="PANKAJ_SAGVEKAR",
        github_token="gho_token",
        branch_name="DEVIONCREW_PANKAJ_SAGVEKAR_AI_FIX",
        start_time=0.0,
        end_time=0.0
    )

def test_score_fast_run_gets_speed_bonus():
    """Runs under 5 min must receive +10 speed bonus."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 120   # 2 min duration
    state.end_time = now
    state.commit_count = 5
    state.final_status = "PASSED"
    state.current_test_results = TestResult(total_failures=0, output="pass")
    result = calculate_score(state)
    assert result["score_calculation"]["speed_bonus"] == 10
    assert result["score_calculation"]["final_score"] == 110

def test_score_slow_run_no_speed_bonus():
    """Runs over 5 min must NOT receive speed bonus."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 400   # 6+ min
    state.end_time = now
    state.commit_count = 3
    state.final_status = "FAILED"
    result = calculate_score(state)
    assert result["score_calculation"]["speed_bonus"] == 0
    assert result["score_calculation"]["final_score"] == 100

def test_score_efficiency_penalty_over_20_commits():
    """Each commit over 20 must subtract 2 from final score."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 400
    state.end_time = now
    state.commit_count = 25   # 5 extra → penalty = 10
    state.final_status = "FAILED"
    result = calculate_score(state)
    assert result["score_calculation"]["efficiency_penalty"] == 10
    assert result["score_calculation"]["final_score"] == 90

def test_score_no_penalty_under_20_commits():
    """Fewer than 20 commits must have zero efficiency penalty."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 100
    state.end_time = now
    state.commit_count = 10
    state.final_status = "PASSED"
    result = calculate_score(state)
    assert result["score_calculation"]["efficiency_penalty"] == 0

def test_score_result_contains_all_required_fields():
    """calculate_score must return all 10 required keys."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 50
    state.end_time = now
    result = calculate_score(state)
    required_keys = [
        "repository_url", "team_name", "leader_name", "branch_name",
        "total_failures", "total_fixes", "iterations_used", "commit_count",
        "final_status", "total_time_seconds", "score_calculation"
    ]
    for key in required_keys:
        assert key in result, f"Missing key in score result: {key}"

def test_score_calculation_keys():
    """score_calculation dict must have exactly 4 keys."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 100
    state.end_time = now
    sc = calculate_score(state)["score_calculation"]
    assert "base_score" in sc
    assert "speed_bonus" in sc
    assert "efficiency_penalty" in sc
    assert "final_score" in sc

def test_score_team_fields_from_state():
    """Score output must reflect team/leader names and branch from state."""
    from app.utils.scoring import calculate_score
    state = _base_state()
    now = time.time()
    state.start_time = now - 10
    state.end_time = now
    result = calculate_score(state)
    assert result["team_name"] == "DEVIONCREW"
    assert result["leader_name"] == "PANKAJ_SAGVEKAR"
    assert result["branch_name"] == "DEVIONCREW_PANKAJ_SAGVEKAR_AI_FIX"
