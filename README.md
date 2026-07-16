# qt-bug-console

Sandbox repo for demoing GitHub Actions ↔ Plane automation.

## Division of labor
- **PR state-sync + PR/commit linking** → Plane's **native GitHub integration** (no code here).
- **Release build stamping** → `.github/workflows/release-stamp.yml`: on a release/dispatch,
  records the build number + artifact link onto a Release Management work item (e.g. `RM-8`)
  and moves it to **Deployed / Live**. This is the piece native can't do.

The full CI/CD handoff package for xuper-app lives on the `ci-cd-integration` branch
under `ci-cd-drafts/` (CI gate, native-vs-custom notes, and the CD stamp).
