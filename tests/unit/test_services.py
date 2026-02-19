import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.git_service import GitService
from app.services.docker_service import DockerService

def test_git_service_clone(tmp_path):
    git_svc = GitService(base_path=str(tmp_path))
    with patch("git.Repo.clone_from") as mock_clone:
        mock_clone.return_value = MagicMock()
        path = git_svc.clone_repo("https://github.com/test/repo", "TEAM1")
        assert "TEAM1_repo" in path
        mock_clone.assert_called_once()

def test_docker_service_sandbox():
    docker_svc = DockerService()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="passed", stderr="", returncode=0)
        output = docker_svc.run_in_sandbox("/tmp/repo", "pytest")
        assert "passed" in output
        mock_run.assert_called_once()
