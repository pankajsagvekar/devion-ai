import time
from typing import Dict, Any
from app.state import AgentState

def calculate_score(state: AgentState) -> Dict[str, Any]:
    total_time = state.end_time - state.start_time
    base_score = 100
    
    # speed_bonus = +10 if <5 min
    speed_bonus = 10 if total_time < 300 else 0
    
    # efficiency_penalty = -2 per commit over 20
    efficiency_penalty = max(0, (state.commit_count - 20) * 2)
    
    final_score = base_score + speed_bonus - efficiency_penalty
    
    results = {
        "repository_url": state.repository_url,
        "team_name": state.team_name,
        "leader_name": state.leader_name,
        "branch_name": state.branch_name,
        "total_failures": state.current_test_results.total_failures if state.current_test_results else 0,
        "total_fixes": len(state.fixes_applied),
        "iterations_used": state.iteration,
        "commit_count": state.commit_count,
        "final_status": state.final_status,
        "total_time_seconds": round(total_time, 2),
        "score_calculation": {
            "base_score": base_score,
            "speed_bonus": speed_bonus,
            "efficiency_penalty": efficiency_penalty,
            "final_score": final_score
        }
    }
    return results
