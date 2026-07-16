# Plane CD — release build stamping

The **non-redundant** piece. Plane's native GitHub integration already moves
work-item state from PR events and links PRs/commits, so we do **not** duplicate
that. What native cannot do is record *which build shipped where* — it has no CI
context. This workflow fills that gap.

## What it does
On a release (tag/`release: published`) or manual dispatch, for a referenced
Release Management item (e.g. `RM-8`):
- adds a **comment**: `🚀 Release <version> — build #<run_number> deployed to <track>`
- adds a **link**: `<track> v<version> (build #<n>)` → the build/artifact URL
- moves the item to **Deployed / Live**

## Files
- `.github/workflows/release-stamp.yml` — `workflow_dispatch` (inputs: rm_ref, version, track) + `release: published` (version = tag, RM ref parsed from release notes).
- `.github/scripts/plane_release_stamp.py` — stdlib-only; resolves the project from the RM key, stamps the build, moves state.

## Secrets
`PLANE_API_TOKEN`, `PLANE_BASE_URL`, `PLANE_WORKSPACE_SLUG`. (No project-id needed — resolved from the `RM-` key.)

## Demo (manual dispatch)
```bash
gh workflow run "Release Stamp (Plane CD)" \
  -f rm_ref=RM-8 -f version=2.1.0 -f track=TestFlight
```
Then refresh the RM board: `RM-8` shows the build comment + link and flips to **Deployed / Live**.

## Verified live
Proven against `test-workspace` RM project (`RM-8` "Release 2.1.0 (CD demo)"):
stamped build #77 → TestFlight comment + link, moved to Deployed / Live.

## Division of labor
| Concern | Owner |
|---|---|
| PR opened/merged → move DEV work item state | **Native Plane integration** |
| Link PR ↔ work item, backlink comments | **Native Plane integration** |
| Record release build # / artifact on RM item, mark Deployed | **This CD workflow** |
