#!/usr/bin/env python3
"""Move a Plane work item and stamp the GitHub build onto it, based on a PR.

Zero third-party deps (uses urllib) so it runs on a bare Actions runner.

Reads configuration from environment variables:
    PLANE_BASE_URL        e.g. https://squad.fyi.fyi
    PLANE_WORKSPACE_SLUG  e.g. test-workspace
    PLANE_PROJECT_ID      UUID of the Plane project
    PLANE_API_TOKEN       Plane API token (sent as the X-API-Key header)
    PR_TITLE              PR title (source of the [ABC-123] reference)
    PR_BRANCH             PR head branch (fallback source, e.g. feature/ABC-123-...)
    TARGET_STATE          Plane state name to move to, e.g. "In Progress" / "Done"

Optional build-tagging vars (set by the workflow; skipped if absent):
    BUILD_NUMBER          GitHub run number, e.g. 42
    RUN_URL               URL of the Actions run
    PR_NUMBER             PR number, for the comment text
    REPO                  owner/repo, for the comment text

Only a *bracketed* reference like [DEVOPS-2] triggers changes, matching Plane's
own convention (unbracketed = link only). Exits 0 without error when no
bracketed reference is present, so unrelated PRs don't fail CI.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

BRACKET_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9]*)-(\d+)\]")
BRANCH_RE = re.compile(r"(?:^|/)([A-Za-z][A-Za-z0-9]*)-(\d+)\b")


def env(name, required=True, default=None):
    val = os.environ.get(name, default)
    if required and not val:
        sys.exit(f"::error::missing required env var {name}")
    return val


def api(method, url, token, body=None, fatal=True):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-API-Key", token)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        msg = f"Plane API {method} {url} -> {e.code}: {e.read().decode()[:300]}"
        if fatal:
            sys.exit(f"::error::{msg}")
        print(f"::warning::{msg}")
        return None


def find_reference(title, branch):
    m = BRACKET_RE.search(title or "")
    if m:
        return m.group(1).upper(), int(m.group(2)), "title (bracketed)"
    m = BRANCH_RE.search(branch or "")
    if m:
        return m.group(1).upper(), int(m.group(2)), "branch"
    return None


def resolve_state_id(base, slug, project, token, target_name):
    url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/states/"
    data = api("GET", url, token)
    states = data.get("results", data if isinstance(data, list) else [])
    for s in states:
        if (s.get("name") or "").strip().lower() == target_name.strip().lower():
            return s["id"]
    names = ", ".join(s.get("name", "?") for s in states)
    sys.exit(f"::error::state '{target_name}' not found in project. Available: {names}")


def find_work_item(base, slug, project, token, seq):
    """Cursor-paginate the project's issues to find the one with this sequence id."""
    base_url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/"
    url = f"{base_url}?per_page=100"
    guard = 0
    while url and guard < 200:
        guard += 1
        data = api("GET", url, token)
        items = data.get("results", data if isinstance(data, list) else [])
        for it in items:
            if it.get("sequence_id") == seq:
                return it
        if isinstance(data, dict) and data.get("next_page_results") and data.get("next_cursor"):
            url = f"{base_url}?per_page=100&cursor={data['next_cursor']}"
        else:
            url = None
    return None


def stamp_build(base, slug, project, token, item_id, key, seq, target, build, run_url, pr_number, repo):
    """Best-effort: add a comment + a link recording the GitHub build."""
    pr_txt = f"PR #{pr_number}" if pr_number else "PR"
    repo_txt = f" in {repo}" if repo else ""
    comment = (
        f"<p>🔧 <b>GitHub CI</b> — build <b>#{build}</b> ({pr_txt}{repo_txt}) "
        f"moved <b>{key}-{seq}</b> to <b>{target}</b>."
    )
    if run_url:
        comment += f' <a href="{run_url}">View run ›</a>'
    comment += "</p>"

    c_url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/{item_id}/comments/"
    if api("POST", c_url, token, {"comment_html": comment}, fatal=False) is not None:
        print(f"Commented build #{build} on {key}-{seq}.")

    if run_url:
        l_url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/{item_id}/links/"
        title = f"CI build #{build} ({target})"
        if api("POST", l_url, token, {"url": run_url, "title": title}, fatal=False) is not None:
            print(f"Linked build #{build} on {key}-{seq}.")


def main():
    base = env("PLANE_BASE_URL").rstrip("/")
    slug = env("PLANE_WORKSPACE_SLUG")
    project = env("PLANE_PROJECT_ID")
    token = env("PLANE_API_TOKEN")
    target = env("TARGET_STATE")
    title = env("PR_TITLE", required=False, default="")
    branch = env("PR_BRANCH", required=False, default="")

    build = env("BUILD_NUMBER", required=False, default="")
    run_url = env("RUN_URL", required=False, default="")
    pr_number = env("PR_NUMBER", required=False, default="")
    repo = env("REPO", required=False, default="")

    ref = find_reference(title, branch)
    if not ref:
        print("No [ABC-123] reference found in PR title or branch — nothing to sync.")
        return
    proj_key, seq, source = ref
    print(f"Found reference {proj_key}-{seq} via {source}; target state '{target}'.")

    state_id = resolve_state_id(base, slug, project, token, target)
    item = find_work_item(base, slug, project, token, seq)
    if not item:
        print(f"::warning::no work item with sequence {seq} in project — skipping.")
        return

    if item.get("state") == state_id:
        print(f"{proj_key}-{seq} already in '{target}'. No change.")
    else:
        url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/{item['id']}/"
        api("PATCH", url, token, {"state": state_id})
        print(f"Moved {proj_key}-{seq} -> '{target}'.")

    if build:
        stamp_build(base, slug, project, token, item["id"], proj_key, seq,
                    target, build, run_url, pr_number, repo)


if __name__ == "__main__":
    main()
