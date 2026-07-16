# xuper-app CI/CD — admin checklist

You (viewer access) can author `ci.yml` and open the PR, but the items below
require **Write** or **Admin/Org Owner**. Hand this list to whoever holds those
roles. Each item notes the minimum role.

## 1. Merge + first run (Write)
- [ ] Review and merge the PR that adds `.github/workflows/ci.yml`.
- [ ] Approve the first workflow run (first-time contributor runs need manual approval).
- [ ] Confirm `format` and `build-test` jobs go green; adjust the `TODO:` lines
      in `ci.yml` (source dirs, Qt version, build system) to match the repo.

## 2. Actions settings (Admin)
- [ ] Settings → Actions → General → allow Actions to run on PRs.
- [ ] Confirm hosted runners are available, or register self-hosted runners if
      builds are too heavy for `ubuntu-latest` / `macos-14`.

## 3. Branch protection / required checks (Admin)
- [ ] Settings → Branches → add rule for `main`.
- [ ] Require status checks to pass before merge; select:
  - [ ] `clang-format`
  - [ ] `Build & unit test (Linux)`
- [ ] Require branches to be up to date before merging (optional but recommended).

## 4. Secrets — only needed for mobile builds / Phase 3 (Admin)
Add under Settings → Secrets and variables → Actions. Names match the `TODO:`s in `ci.yml`.

Android:
- [ ] `ANDROID_KEYSTORE_BASE64` — base64 of the release keystore
- [ ] `ANDROID_KEYSTORE_PASSWORD`
- [ ] `ANDROID_KEY_ALIAS`
- [ ] `ANDROID_KEY_PASSWORD`
- [ ] `PLAY_SERVICE_ACCOUNT_JSON` — for Play internal-track upload (Phase 3)

iOS / Apple:
- [ ] `APPLE_CERTIFICATE_BASE64` + `APPLE_CERTIFICATE_PASSWORD`
- [ ] `APPLE_PROVISIONING_PROFILE_BASE64`
- [ ] `APP_STORE_CONNECT_KEY_ID` / `_ISSUER_ID` / `_PRIVATE_KEY` — for TestFlight (Phase 3)

## 5. Enable mobile jobs (Write, after secrets exist)
- [ ] In `ci.yml`, change `if: false` on the `android` / `ios` jobs to a real
      condition (e.g. `if: github.ref == 'refs/heads/main'`).
- [ ] Add the actual build steps where the `TODO:` placeholders are.

## 6. Plane ↔ GitHub (Org Owner) — Phase 1 dependency
- [ ] Connect the **Plane GitHub App** to the org and grant access to `xuper-app`.
  (Org-level install — a repo admin is not enough.)
- [ ] Map `xuper-app` PR states → **Devs** states in Plane workspace settings.
- [ ] Create the `plane` label on GitHub and `github` label in Plane.

## Access you should request for yourself
- **Write** on `xuper-app` → merge workflows, manage/approve runs, edit `ci.yml`.
- **Admin** (or an owner acting for you) → secrets + branch protection.
- **Org Owner** action → the Plane GitHub App connection (Phase 1).
