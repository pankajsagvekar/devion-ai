import pytest
import time
from app.state import AgentState, TestResult
from app.utils.scoring import calculate_score

def test_calculate_score_fast_pass(sample_agent_state):
    sample_agent_state.start_time = time.time() - 100 # 100 seconds ago
    sample_agent_state.end_time = time.time()
    sample_agent_state.current_test_results = TestResult(total_failures=0, output="pass")
    sample_agent_state.commit_count = 5
    sample_agent_state.final_status = "PASSED"
    sample_agent_state.iteration = 1
    
    results = calculate_score(sample_agent_state)
    assert results["score_calculation"]["speed_bonus"] == 10
    assert results["score_calculation"]["efficiency_penalty"] == 0
    assert results["score_calculation"]["final_score"] == 110

def test_calculate_score_slow_fail(sample_agent_state):
    sample_agent_state.start_time = time.time() - 400 # 400 seconds ago
    sample_agent_state.end_time = time.time()
    sample_agent_state.commit_count = 25 # Penalty expected
    sample_agent_state.final_status = "FAILED"
    
    results = calculate_score(sample_agent_state)
    assert results["score_calculation"]["speed_bonus"] == 0
    assert results["score_calculation"]["efficiency_penalty"] == 10 # (25-20)*2
    assert results["score_calculation"]["final_score"] == 90
