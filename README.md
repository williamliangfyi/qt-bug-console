# qt-bug-console

Sandbox repo for demoing GitHub Actions -> Plane automation.

- `.github/workflows/plane-sync.yml` moves a Plane work item and stamps the
  GitHub build number onto it when a PR references `[DEVOPS-<n>]` in its title.
- `ci-cd-drafts/` (on the `ci-cd-integration` branch) holds the full CI/CD
  handoff package for xuper-app.
