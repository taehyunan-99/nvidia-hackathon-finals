#!/usr/bin/env bash
# Adapted from agentic-project-init: delegate safe staged-content handling to Python.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
exec python3 "$repo_root/scripts/sync_guides.py" "$@"
