from app.graph import create_graph
from app.state import AgentState
import asyncio
import time

async def test_run():
    print("--- STARTING MOCKED DRY RUN ---")
    initial_state = AgentState(
        repository_url="https://github.com/dummy/repo",
        team_name="Antigravity",
        leader_name="Test User!!", # Contains special chars/spaces
        branch_name="ANTIGRAVITY_TESTUSER_AI_FIX", # Pre-sanitized for direct test
        start_time=time.time(),
        repo_path="/tmp/repos/mock_repo"
    )
    
    import os
    os.makedirs("/tmp/repos/mock_repo", exist_ok=True)
    with open("/tmp/repos/mock_repo/test.py", "w") as f:
        f.write("def func():\n  return 1/0\n")
    
    # We will override the fix_generator to just pretend it did work
    graph = create_graph()
    
    print("Executing Graph...")
    try:
        final_output = await graph.ainvoke(initial_state)
        
        print("\n=== DRY RUN RESULTS ===")
        print(f"Branch Triggered: {final_output['branch_name']}")
        print(f"Final Status: {final_output['final_status']}")
        for k,v in final_output['results_json'].items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"Graph exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_run())
