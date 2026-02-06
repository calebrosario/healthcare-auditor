#!/bin/bash
# Isolated test runner to avoid Python caching issues

# Set PYTHONPATH to include worktree backend directory (NOT parent backend)
export PYTHONPATH="/Users/calebrosario/Documents/sandbox/healthcare-auditor/.worktrees/fraud-detection-ml/backend:$PYTHONPATH"

# Clear Python caches
find . -type d -name '__pycache__' -delete
find . -type f -name '*.pyc' -delete

# Run pytest with specific test file
pytest "$@" -v --tb=short
