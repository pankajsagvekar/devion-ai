import time
import os
from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.agents.orchestrator import orchestrator_agent
from app.agents.test_runner import test_runner_agent
from app.agents.analyzer import analyzer_agent
from app.agents.fix_generator import fix_generator_agent
from app.agents.git_agent import git_agent
from app.utils.scoring import calculate_score

def create_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("orchestrator", orchestrator_agent)
    workflow.add_node("tester", test_runner_agent)
    workflow.add_node("analyzer", analyzer_agent)
    workflow.add_node("fixer", fix_generator_agent)
    workflow.add_node("git", git_agent)

    # Define Edges & Conditional Logic
    workflow.set_entry_point("orchestrator")
    
    def orchestrator_route(state: AgentState):
        if state.final_status in ["PASSED", "FAILED"]:
            return "end"
        return "test"

    workflow.add_conditional_edges(
        "orchestrator",
        orchestrator_route,
        {
            "test": "tester",
            "end": "finalize"
        }
    )

    def after_test_route(state: AgentState):
        if state.current_test_results and state.current_test_results.total_failures == 0:
            return "end"
        if state.iteration >= state.max_retries or state.final_status == "FAILED":
            return "end"
        return "analyze"

    workflow.add_conditional_edges(
        "tester",
        after_test_route,
        {
            "analyze": "analyzer",
            "end": "git"  # Move to Git commit at the end
        }
    )

    workflow.add_edge("analyzer", "fixer")
    workflow.add_edge("fixer", "orchestrator") # Loop back without committing
    workflow.add_edge("git", "finalize")

    # Finalization node to generate results.json
    async def finalize_results(state: AgentState):
        import json
        
        # Determine final status if not already set (e.g. by a fatal AI error)
        if state.final_status == "PENDING":
            if state.current_test_results and state.current_test_results.total_failures == 0:
                state.final_status = "PASSED"
            else:
                state.final_status = "FAILED"

        state.end_time = time.time()
        state.results_json = calculate_score(state)
        
        # Save results.json to the repository path for hackathon compliance
        if state.repo_path and os.path.exists(state.repo_path):
            results_file = os.path.join(state.repo_path, "results.json")
            try:
                with open(results_file, "w") as f:
                    json.dump(state.results_json, f, indent=2)
                print(f"DEBUG: Successfully generated {results_file}")
            except Exception as e:
                print(f"ERROR saving results.json: {e}")

        return state

    workflow.add_node("finalize", finalize_results)
    workflow.add_edge("finalize", END)

    return workflow.compile()
