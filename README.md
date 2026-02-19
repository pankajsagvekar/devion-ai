# Autonomous CI/CD Healing Agent

A multi-agent system built with LangGraph and FastAPI that autonomously clones a repository, runs tests, analyzes failures, and pushes fixes.

## Prerequisites

- Python 3.10+
- Docker (for sandbox execution)
- Git

## Installation

1. Set up a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the required Python packages:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. (Optional) Install `pytest-json-report` for detailed test analysis:
   ```bash
   pip install pytest-json-report
   ```

## Running the Application

### Locally

Start the FastAPI server:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
python3 backend/app/main.py
```

The API will be available at `http://localhost:8000`.

### Via Docker

Build and run the container:

```bash
docker build -t devion-ai -f backend/Dockerfile .
docker run -p 8000:8000 devion-ai
```

## Using the API

Trigger the autonomous healing workflow by sending a POST request to `/run-agent`:

```bash
curl -X POST http://localhost:8000/run-agent \
     -H "Content-Type: application/json" \
     -d '{
           "repository_url": "https://github.com/your-repo/demo",
           "team_name": "Antigravity",
           "leader_name": "Pankaj"
         }'
```

### Response

The endpoint returns a structured JSON with:

- `repository_url`
- `branch_name` (Format: `TEAM_LEADER_AI_FIX`)
- `final_status` (`PASSED` or `FAILED`)
- `score_calculation` (Hackathon-specific scoring)

## Project Structure

- `/app/agents`: Logic for Orchestrator, Analyzer, Fixer, Git, and Tester.
- `/app/services`: Core services for Git and Docker operations.
- `/app/utils`: Scoring and logging utilities.
- `graph.py`: LangGraph workflow definition.
- `state.py`: Pydantic models for agent state management.
