#!/usr/bin/env python3
"""Stamp a release build onto a Plane Release Management work item.

This is the CD counterpart to native GitHub↔Plane sync. Native moves work-item
state from PR events but has no CI context — it cannot record which *build* shipped
where. This script does exactly that: on a release it adds a build comment + an
artifact link to the RM work item and (optionally) moves it to a deployed state.

Zero third-party deps (urllib) so it runs on a bare Actions runner.

Environment:
    PLANE_BASE_URL        e.g. https://squad.fyi.fyi
    PLANE_WORKSPACE_SLUG  e.g. test-workspace
    PLANE_API_TOKEN       Plane API token (X-API-Key header)

    RM_REF                work item to stamp, e.g. "RM-8" (project key + sequence)
    VERSION               release version, e.g. "2.1.0"
    TRACK                 destination, e.g. "TestFlight" / "Play internal"
    BUILD_NUMBER          GitHub run number
    RUN_URL               Actions run URL
    ARTIFACT_URL          optional link to the uploaded build (defaults to RUN_URL)
    DEPLOY_STATE          optional state to move the item to, e.g. "Deployed / Live"
                          (leave empty to only stamp, not move)

If RM_REF is empty, RELEASE_BODY is scanned for a [RM-x] reference.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

REF_RE = re.compile(r"\[?([A-Za-z][A-Za-z0-9]*)-(\d+)\]?")


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


def parse_ref(rm_ref, release_body):
    src = rm_ref or release_body or ""
    m = REF_RE.search(src)
    if not m:
        return None
    return m.group(1).upper(), int(m.group(2))


def resolve_project(base, slug, token, key):
    data = api("GET", f"{base}/api/v1/workspaces/{slug}/projects/", token)
    for p in data.get("results", data if isinstance(data, list) else []):
        if (p.get("identifier") or "").upper() == key:
            return p["id"]
    sys.exit(f"::error::no project with identifier '{key}'")


def find_item(base, slug, project, token, seq):
    base_url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/"
    url = f"{base_url}?per_page=100"
    guard = 0
    while url and guard < 200:
        guard += 1
        data = api("GET", url, token)
        for it in data.get("results", data if isinstance(data, list) else []):
            if it.get("sequence_id") == seq:
                return it
        if isinstance(data, dict) and data.get("next_page_results") and data.get("next_cursor"):
            url = f"{base_url}?per_page=100&cursor={data['next_cursor']}"
        else:
            url = None
    return None


def resolve_state(base, slug, project, token, name):
    data = api("GET", f"{base}/api/v1/workspaces/{slug}/projects/{project}/states/", token)
    states = data.get("results", data if isinstance(data, list) else [])
    for s in states:
        if (s.get("name") or "").strip().lower() == name.strip().lower():
            return s["id"]
    avail = ", ".join(s.get("name", "?") for s in states)
    sys.exit(f"::error::state '{name}' not found. Available: {avail}")


def main():
    base = env("PLANE_BASE_URL").rstrip("/")
    slug = env("PLANE_WORKSPACE_SLUG")
    token = env("PLANE_API_TOKEN")

    version = env("VERSION")
    track = env("TRACK", required=False, default="build")
    build = env("BUILD_NUMBER", required=False, default="")
    run_url = env("RUN_URL", required=False, default="")
    artifact = env("ARTIFACT_URL", required=False, default="") or run_url
    deploy_state = env("DEPLOY_STATE", required=False, default="")
    rm_ref = env("RM_REF", required=False, default="")
    release_body = env("RELEASE_BODY", required=False, default="")

    ref = parse_ref(rm_ref, release_body)
    if not ref:
        print("No [RM-x] reference provided — nothing to stamp.")
        return
    key, seq = ref
    print(f"Stamping {key}-{seq}: v{version} build #{build} -> {track}")

    project = resolve_project(base, slug, token, key)
    item = find_item(base, slug, project, token, seq)
    if not item:
        print(f"::warning::no work item {key}-{seq} — skipping.")
        return

    build_txt = f"build <b>#{build}</b>" if build else "build"
    comment = f"<p>🚀 <b>Release {version}</b> — {build_txt} deployed to <b>{track}</b>."
    if artifact:
        comment += f' <a href="{artifact}">View build ›</a>'
    comment += "</p>"
    c_url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/{item['id']}/comments/"
    if api("POST", c_url, token, {"comment_html": comment}, fatal=False) is not None:
        print("  commented.")

    l_url = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/{item['id']}/links/"
    title = f"{track} v{version} (build #{build})" if build else f"{track} v{version}"
    if api("POST", l_url, token, {"url": artifact, "title": title}, fatal=False) is not None:
        print("  linked.")

    if deploy_state:
        sid = resolve_state(base, slug, project, token, deploy_state)
        if item.get("state") != sid:
            u = f"{base}/api/v1/workspaces/{slug}/projects/{project}/issues/{item['id']}/"
            api("PATCH", u, token, {"state": sid})
            print(f"  moved {key}-{seq} -> '{deploy_state}'.")
        else:
            print(f"  {key}-{seq} already in '{deploy_state}'.")


if __name__ == "__main__":
    main()
