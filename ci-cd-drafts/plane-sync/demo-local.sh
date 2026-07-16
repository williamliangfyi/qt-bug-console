#!/usr/bin/env bash
# Live screen-share driver for the PR -> Plane demo (no GitHub needed).
# It calls the SAME plane_sync.py the workflow uses, so what the room sees is
# exactly what the Action would do.
#
# Usage:
#   export PLANE_API_TOKEN=plane_api_xxx          # your token (required)
#   ./demo-local.sh                                # uses sandbox defaults below
#
# Screen-share both this terminal and the Plane board; press Enter to advance
# each stage and refresh the board to show the ticket move.
set -euo pipefail
cd "$(dirname "$0")"

: "${PLANE_API_TOKEN:?export PLANE_API_TOKEN first}"
export PLANE_BASE_URL="${PLANE_BASE_URL:-https://squad.fyi.fyi}"
export PLANE_WORKSPACE_SLUG="${PLANE_WORKSPACE_SLUG:-test-workspace}"
export PLANE_PROJECT_ID="${PLANE_PROJECT_ID:-888fb3ce-2574-42f7-bbca-bb57e789bf0c}"
TICKET="${TICKET:-DEVOPS-2}"
PY="${PYTHON:-python3}"
SCRIPT=".github/scripts/plane_sync.py"

board="$PLANE_BASE_URL/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID/issues/"
echo "Board: $board"
echo "Ticket for demo: $TICKET"
echo

read -r -p "STAGE 1 - ticket should be in Todo. Press Enter to 'open the PR' -> In Progress..."
PR_TITLE="[$TICKET] demo fix" PR_BRANCH="feature/${TICKET}-demo" TARGET_STATE="In Progress" "$PY" "$SCRIPT"
echo ">> Refresh the board: $TICKET should now be In Progress."
echo

read -r -p "STAGE 2 - Press Enter to 'merge the PR' -> Done..."
PR_TITLE="[$TICKET] demo fix" PR_BRANCH="feature/${TICKET}-demo" TARGET_STATE="Done" "$PY" "$SCRIPT"
echo ">> Refresh the board: $TICKET should now be Done."
echo

read -r -p "STAGE 3 (optional) - Press Enter to reset $TICKET back to Todo for the next run..."
PR_TITLE="[$TICKET] reset" PR_BRANCH="x" TARGET_STATE="Todo" "$PY" "$SCRIPT"
echo ">> $TICKET reset to Todo. Demo ready to run again."
