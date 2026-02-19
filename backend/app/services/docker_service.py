import subprocess
import os

class DockerService:
    def __init__(self, image_name: str = "python:3.10-slim"):
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

    def run_in_sandbox(self, repo_path: str, command: str) -> str:
        # Placeholder for real Docker sandbox execution
        # Logic: docker run -v repo_path:/app -w /app image_name command
        container_cmd = [
            "docker", "run", "--rm",
            "-v", f"{repo_path}:/app",
            "-w", "/app",
            self.image_name,
            "sh", "-c", f"pip install pytest pytest-json-report && {command}"
        ]
        try:
            result = subprocess.run(container_cmd, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
