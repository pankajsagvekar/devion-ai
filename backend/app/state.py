from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BugMetadata(BaseModel):
    file_name: str
    line_number: int
    error_message: str
    bug_type: str  # LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, INDENTATION
    action: str = "FIX"  # FIX or DELETE

class TestResult(BaseModel):
    total_failures: int
    failures: List[BugMetadata] = []
    output: str

class AgentState(BaseModel):
    # Input data
    repository_url: str
    team_name: str
    leader_name: str
    github_token: str = ""
    
    # Workflow data
    branch_name: str = ""
    repo_path: str = ""
    iteration: int = 0
    max_retries: int = 5
    
    # State tracking
    current_test_results: Optional[TestResult] = None
    fixes_applied: List[str] = []
    commit_count: int = 0
    
    # Final Result
    final_status: str = "PENDING"  # PASSED / FAILED
    start_time: float = 0.0
    end_time: float = 0.0
    results_json: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True
