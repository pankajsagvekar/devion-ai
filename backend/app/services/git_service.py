import os
import git
from typing import Optional

class GitService:
    def __init__(self, base_path: str = "/tmp/repos"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def clone_repo(self, repo_url: str, team_name: str) -> str:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_path = os.path.join(self.base_path, f"{team_name}_{repo_name}")
        
        if os.path.exists(target_path):
            repo = git.Repo(target_path)
        else:
            repo = git.Repo.clone_from(repo_url, target_path)
        
        return target_path

    def create_branch(self, repo_path: str, branch_name: str):
        repo = git.Repo(repo_path)
        if branch_name in repo.heads:
            repo.git.checkout(branch_name)
        else:
            new_branch = repo.create_head(branch_name)
            repo.git.checkout(new_branch)

    def commit_and_push(self, repo_path: str, branch_name: str, message: str):
        repo = git.Repo(repo_path)
        repo.git.add(A=True)
        if repo.is_dirty():
            repo.index.commit(f"[AI-AGENT] {message}")
            origin = repo.remote(name='origin')
            origin.push(branch_name)
        else:
            print("No changes to commit.")
