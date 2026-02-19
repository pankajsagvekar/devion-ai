import subprocess
import os

class DockerService:
    def __init__(self, image_name: str = "devion-sandbox"):
        self.image_name = image_name

    def run_tests(self, repo_path: str) -> str:
        # Simple execution for now, assuming pytest is installed
        # In a real scenario, this would use docker-py to run in a sandbox
        try:
            result = subprocess.run(
                ["pytest", "--json-report", "--json-report-file=report.json"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def run_local(self, repo_path: str, command: str) -> str:
        # Executes command directly on the host (no isolation)
        print(f"DEBUG: Running LOCAL command in {repo_path}: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def run_in_sandbox(self, repo_path: str, command: str) -> str:
        # Use the pre-built devion-sandbox image
        container_cmd = [
            "docker", "run", "--rm",
            "-v", f"{repo_path}:/app",
            "-w", "/app",
            self.image_name,
            "sh", "-c", command
        ]
        print(f"DEBUG: Running sandbox command: {' '.join(container_cmd)}")
        try:
            result = subprocess.run(container_cmd, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
