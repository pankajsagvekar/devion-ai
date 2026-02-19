import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.git_service import GitService
from app.services.docker_service import DockerService


# ─────────────────────────────────────────────────────────────
# GitService
# ─────────────────────────────────────────────────────────────

def test_git_service_authenticated_url_with_token():
    """URL must embed token correctly for HTTPS repos."""
    svc = GitService()
    url = svc._get_authenticated_url("https://github.com/org/repo.git", "gho_mytoken")
    assert "gho_mytoken@github.com" in url

def test_git_service_authenticated_url_without_token():
    """URL must remain unchanged when no token provided."""
    svc = GitService()
    url = svc._get_authenticated_url("https://github.com/org/repo.git", "")
    assert url == "https://github.com/org/repo.git"

def test_git_service_clone_with_token(tmp_path):
    """clone_repo must use the authenticated URL when a token is given."""
    svc = GitService(base_path=str(tmp_path))
    with patch("git.Repo.clone_from") as mock_clone:
        mock_clone.return_value = MagicMock()
        svc.clone_repo("https://github.com/org/repo.git", "DEVIONCREW", token="gho_token")
        call_url = mock_clone.call_args[0][0]
        assert "gho_token@github.com" in call_url

def test_git_service_clone_without_token(tmp_path):
    """clone_repo must use the original URL when no token is given."""
    svc = GitService(base_path=str(tmp_path))
    with patch("git.Repo.clone_from") as mock_clone:
        mock_clone.return_value = MagicMock()
        svc.clone_repo("https://github.com/org/repo.git", "DEVIONCREW", token="")
        call_url = mock_clone.call_args[0][0]
        assert "https://github.com/org/repo.git" == call_url

def test_git_service_clone_reuses_existing_repo(tmp_path):
    """clone_repo must reuse existing path without re-cloning."""
    repo_path = tmp_path / "DEVIONCREW_repo"
    repo_path.mkdir()
    svc = GitService(base_path=str(tmp_path))
    with patch("git.Repo") as mock_repo, \
         patch("git.Repo.clone_from") as mock_clone:
        mock_repo.return_value = MagicMock()
        svc.clone_repo("https://github.com/org/repo.git", "DEVIONCREW")
        mock_clone.assert_not_called()

def test_git_service_commit_and_push_with_token(tmp_path):
    """commit_and_push must update remote URL with token before pushing."""
    svc = GitService()
    mock_repo = MagicMock()
    mock_repo.is_dirty.return_value = True
    mock_origin = MagicMock()
    mock_origin.url = "https://github.com/org/repo.git"
    mock_repo.remote.return_value = mock_origin
    with patch("git.Repo", return_value=mock_repo):
        svc.commit_and_push("/tmp/repo", "DEVIONCREW_AI_FIX", "Fix msg", token="gho_token")
        mock_origin.set_url.assert_called_once()
        set_url_arg = mock_origin.set_url.call_args[0][0]
        assert "gho_token@github.com" in set_url_arg
        mock_origin.push.assert_called_once()

def test_git_service_commit_skips_on_clean_repo(tmp_path):
    """commit_and_push must skip commit if repo has no changes."""
    svc = GitService()
    mock_repo = MagicMock()
    mock_repo.is_dirty.return_value = False
    with patch("git.Repo", return_value=mock_repo):
        svc.commit_and_push("/tmp/repo", "branch", "msg", token="")
        mock_repo.index.commit.assert_not_called()


# ─────────────────────────────────────────────────────────────
# DockerService
# ─────────────────────────────────────────────────────────────

def test_docker_service_run_in_sandbox_success():
    """run_in_sandbox must return combined stdout+stderr output."""
    svc = DockerService()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="2 passed", stderr="", returncode=0)
        output = svc.run_in_sandbox("/tmp/repo", "pytest")
        assert "passed" in output

def test_docker_service_run_in_sandbox_failure():
    """run_in_sandbox must return output even on test failure exit code."""
    svc = DockerService()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="1 failed", stderr="FAILED test.py", returncode=1)
        output = svc.run_in_sandbox("/tmp/repo", "pytest")
        assert "failed" in output

def test_docker_service_run_in_sandbox_exception_handled():
    """run_in_sandbox must return error message string on exception."""
    svc = DockerService()
    with patch("subprocess.run", side_effect=FileNotFoundError("docker not found")):
        output = svc.run_in_sandbox("/tmp/repo", "pytest")
        assert "docker not found" in output.lower() or len(output) > 0

def test_docker_service_uses_correct_image():
    """DockerService must use python:3.10-slim by default."""
    svc = DockerService()
    assert svc.image_name == "python:3.10-slim"

def test_docker_service_custom_image():
    """DockerService must accept a custom Docker image name."""
    svc = DockerService(image_name="python:3.9-slim")
    assert svc.image_name == "python:3.9-slim"
