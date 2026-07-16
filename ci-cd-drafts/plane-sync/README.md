# Plane Sync — live demo (approach C: custom API bot)

Demonstrates "open a PR → the Plane ticket moves itself." Runs entirely inside a
**personal fork** + a **sandbox Plane workspace**, so it needs no org-owner
access and never touches live `DEVS` tickets.

> Production note: your team plan prefers Plane's **native** GitHub integration
> (no secrets, no maintenance). This custom bot is the *demoable* version you can
> stand up solo. See `../ADMIN_CHECKLIST.md` for the native path.

## Files
- `.github/workflows/plane-sync.yml` — triggers on PR events, sets target state.
- `.github/scripts/plane_sync.py` — stdlib-only; finds `[ABC-123]` in the PR title/branch and PATCHes the work item's state.

## One-time setup (in your personal fork)

1. **Fork** the repo (you become admin of the fork).
2. Add **4 repo secrets** — Settings → Secrets and variables → Actions → *Secrets*:

   | Secret | Demo value |
   |---|---|
   | `PLANE_API_TOKEN` | your Plane API token |
   | `PLANE_BASE_URL` | `https://squad.fyi.fyi` |
   | `PLANE_WORKSPACE_SLUG` | `test-workspace` |
   | `PLANE_PROJECT_ID` | `888fb3ce-2574-42f7-bbca-bb57e789bf0c`  (test-workspace → DevOps project) |

3. Commit `.github/workflows/plane-sync.yml` + `.github/scripts/plane_sync.py` to `main` of the fork.

A ready demo ticket already exists in the sandbox: **`DEVOPS-2` — "[DEMO] CI/CD Plane sync test ticket"**, currently in **Todo**.

## The 3-step demo script

**Step 1 — show the board (1 min).** Open the sandbox DevOps board; point out `DEVOPS-2` in **Todo**.

**Step 2 — trigger it (2 min).**
```bash
git checkout -b feature/DEVOPS-2-demo-fix
echo >> README.md            # trivial change
git commit -am "docs: trivial change for demo"
git push -u origin feature/DEVOPS-2-demo-fix
```
Open a PR **within your fork** titled: `[DEVOPS-2] demo fix`.
(The brackets are what trigger the state change — matching Plane's own convention.)

**Step 3 — the payoff (2 min).**
- **Actions** tab → the *Plane Sync* run goes green.
- Switch to Plane, refresh → `DEVOPS-2` has moved **Todo → In Progress**.
- Merge the PR → it moves **→ Done** (merged PRs map to `Done`).

## Talking points for the room
- **Head of Engineering:** developers never manually update tickets; the PR is the source of truth. Only bracketed `[ABC-123]` refs move state, so it's predictable.
- **DevOps:** no hardcoded credentials — the token lives only in GitHub's encrypted secrets, read at runtime. Two caveats to raise proactively:
  - `pull_request` from an *outside* fork gets **no secrets** (GitHub security) — fine for this same-fork demo; for real cross-fork contributions you'd use the native integration or `pull_request_target` (with its risks).
  - This is a bot we maintain; the **native Plane integration** does the same thing with zero code — recommend it for production.

## Verified
This script was tested against `DEVOPS-2`: PR title `[DEVOPS-2] …` moved it Todo→In Progress, was idempotent on re-run, and reset cleanly. State UUIDs in the DevOps project: Todo `8464758a…`, In Progress `16165fcc…`, Done `2c82b407…`.
