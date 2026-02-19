import os
import git
from typing import Optional

class GitService:
    def __init__(self, base_path: str = "/tmp/repos"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_authenticated_url(self, repo_url: str, token: str) -> str:
        if not token:
            return repo_url
        
        import re
        # Strip any existing credentials (everything between https:// and the last @ before the host)
        clean_url = re.sub(r"https://[^/]*@", "https://", repo_url)
        
        # Add the token
        if clean_url.startswith("https://"):
            return clean_url.replace("https://", f"https://{token}@")
        return clean_url

    def clone_repo(self, repo_url: str, team_name: str, token: str = "") -> str:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_path = os.path.join(self.base_path, f"{team_name}_{repo_name}")
        print(f"DEBUG: Cloning to {target_path}")
        
        auth_url = self._get_authenticated_url(repo_url, token)
        
        if os.path.exists(target_path):
            print(f"DEBUG: Path {target_path} exists, using existing repo")
            repo = git.Repo(target_path)
            # CRITICAL: Always update the remote URL if a token is provided to fix previous corruptions
            if token:
                origin = repo.remote(name='origin')
                auth_url = self._get_authenticated_url(origin.url, token)
                origin.set_url(auth_url)
        else:
            print(f"DEBUG: Cloning from {auth_url}")
            repo = git.Repo.clone_from(auth_url, target_path)
        
        return target_path

    def create_branch(self, repo_path: str, branch_name: str, token: str = ""):
        print(f"DEBUG: Creating/checking out branch {branch_name} in {repo_path}")
        repo = git.Repo(repo_path)
        
        # Ensure remote URL is fresh
        if token:
            origin = repo.remote(name='origin')
            auth_url = self._get_authenticated_url(origin.url, token)
            origin.set_url(auth_url)

        # Ensure we are on a clean state (handle main or master)
        default_branch = 'main' if 'main' in [head.name for head in repo.heads] else 'master'
        print(f"DEBUG: Checking out default branch: {default_branch}")
        repo.git.checkout(default_branch)
        repo.git.pull()

        if branch_name in repo.heads:
            print(f"DEBUG: Branch {branch_name} exists, checking out.")
            repo.git.checkout(branch_name)
        else:
            print(f"DEBUG: Creating new branch {branch_name}")
            new_branch = repo.create_head(branch_name)
            repo.git.checkout(new_branch)

    def commit_and_push(self, repo_path: str, branch_name: str, message: str, token: str = ""):
        print(f"DEBUG: GitService committing changes to {branch_name}...")
        repo = git.Repo(repo_path)
        repo.git.add(A=True)
        if repo.is_dirty():
            repo.index.commit(f"[AI-AGENT] {message}")
            print(f"DEBUG: Commit successful: [AI-AGENT] {message}")
            
            # Update remote URL with token if provided for the push
            origin = repo.remote(name='origin')
            if token:
                auth_url = self._get_authenticated_url(origin.url, token)
                origin.set_url(auth_url)
            
            print(f"DEBUG: Pushing to {branch_name}...")
            origin.push(branch_name)
            print("DEBUG: Push successful.")
        else:
            print("DEBUG: No changes detected to commit.")
