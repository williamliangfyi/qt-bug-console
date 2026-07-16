# xuper-app CI — DevOps handoff

A plug-and-play GitHub Actions quality gate. Copy two files into the repo and it
runs on every PR: **clang-format** check + **build & unit tests** (auto-detects
CMake or qmake). No edits to the workflow are required in the common case.

## What's in this package

| Path | Purpose |
|---|---|
| `.github/workflows/ci.yml` | The workflow. Auto-detects build system, reads Qt version from a repo variable. |
| `.clang-format` | Recommended style (LLVM, 4-space, 100 col). Commit at repo root so formatting is deterministic. |
| `ADMIN_CHECKLIST.md` | Admin/Org-Owner tasks: branch protection, secrets, mobile signing, Plane↔GitHub. |
| `sample/` | Self-contained proof: run `./sample/run-ci-local.sh` to see the exact jobs pass locally, no GitHub needed. |

## Plug-and-play: 3 steps for DevOps

1. **Copy** into the `xuper-app` repo root:
   - `.github/workflows/ci.yml`
   - `.clang-format`  (skip if the repo already has one it prefers)
2. **(Optional) set the Qt version** — Settings → Secrets and variables → Actions → **Variables** → new variable `QT_VERSION` (e.g. `6.11.*`). If unset, the workflow defaults to `6.11.*`.
3. **Open a PR / push to `main`.** The `clang-format` and `Build & unit test (Linux)` checks run automatically.

That's it for the gate. To make the checks **required** before merge, add a branch-protection rule (see `ADMIN_CHECKLIST.md`).

## What's automatic vs. what may need a tweak

Automatic:
- **Build system detection** — uses `CMakeLists.txt` if present, else a root `*.pro` (qmake).
- **Qt install** — via `jurplel/install-qt-action`, version from `QT_VERSION` variable.
- **Tests** — runs `ctest`; passes cleanly if there are no tests yet (`--no-tests=ignore`).
- **Submodules** — checked out recursively.

May need a one-line tweak (only if the defaults don't fit):
- Build entrypoint isn't at repo root, or needs extra CMake flags → edit the `Build & test (CMake)` step.
- Repo needs system deps beyond Qt → add an `apt-get install` step.
- Formatting shouldn't block merges yet → add `continue-on-error: true` to the `format` job.

## Mobile builds (Android / iOS)

Included but **disabled** (`if: false`) because they need runners + signing secrets
that only an admin can provision. Enabling them is documented step-by-step in
`ADMIN_CHECKLIST.md` (§4 secrets, §5 enable jobs).

## Verify locally before handoff

```bash
cd sample
./run-ci-local.sh          # RED: format fails, build+tests pass (exit 1)
./run-ci-local.sh --fix    # GREEN: all pass (exit 0)
```
This runs the same commands the workflow runs (`clang-format --dry-run --Werror`,
then `cmake` + `ctest`), so you can demonstrate the gate without pushing anything.
