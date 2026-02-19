import os
import sys
from dotenv import load_dotenv

# Add the backend directory to sys.path to import GitService
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.git_service import GitService

def test_git_flow():
    load_dotenv()
    
    # Configuration
    token = os.getenv("GITHUB_TOKEN") or input("Enter your GitHub token: ").strip()
    repo_url = os.getenv("TEST_REPO_URL") or input("Enter your repo URL (e.g., https://github.com/user/repo): ").strip()
    team_name = "TEST_FLOW"
    branch_name = "verify_git_auth_test"
    
    if not token or not repo_url:
        print("ERROR: Token and Repo URL are required.")
        return

    git_svc = GitService("/tmp/git_verify")
    
    print("\n--- STARTING GIT VERIFICATION ---")
    
    try:
        # 1. Clone
        print(f"1. Cloning {repo_url}...")
        repo_path = git_svc.clone_repo(repo_url, team_name, token)
        print(f"   SUCCESS: Cloned to {repo_path}")
        
        # 2. Create Branch
        print(f"2. Creating branch {branch_name}...")
        git_svc.create_branch(repo_path, branch_name, token)
        print(f"   SUCCESS: Branch created and checked out.")
        
        # 3. Dummy Change
        test_file = os.path.join(repo_path, "git_verify.txt")
        with open(test_file, "w") as f:
            f.write(f"Verification successful. Time: {os.times()}")
        
        # 4. Commit and Push
        print(f"3. Committing and Pushing to {branch_name}...")
        git_svc.commit_and_push(repo_path, branch_name, "Git Verification Test", token)
        
        print("\n--- ALL STEPS COMPLETED SUCCESSFULLY! ---")
        print(f"Check your repo: {repo_url}/tree/{branch_name}")
        
    except Exception as e:
        print(f"\nFATAL ERROR during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_git_flow()
