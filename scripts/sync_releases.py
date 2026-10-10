#!/usr/bin/env python3
"""Generate Scoop and Homebrew manifests from per-app GitHub Releases.

Python 3.11+, standard library only. No downloaded software is executed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
PLACEHOLDER = re.compile(r"@@([A-Z0-9_]+)@@")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")


class SyncError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise SyncError(message)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SyncError(f"Cannot read JSON {path}: {exc}") from exc


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=4) + "\n"


def inside(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), f"Path escapes repository: {relative}")
    return path


def version_key(version):
    require(isinstance(version, str) and VERSION.fullmatch(version),
            f"Expected numeric version X.Y.Z or X.Y.Z.N, got {version!r}")
    parts = tuple(map(int, version.split(".")))
    return parts + (0,) * (4 - len(parts))


def load_apps(root):
    apps = []
    for path in sorted((root / "apps").glob("*.json")):
        app = read_json(path)
        require(isinstance(app, dict), f"{path.name}: expected an object")
        require(not (set(app) - {"schema_version", "id", "enabled", "scoop", "homebrew"}),
                f"{path.name}: unknown configuration keys")
        require(app.get("schema_version") == 1, f"{path.name}: schema_version must be 1")
        app_id = app.get("id", "")
        require(isinstance(app_id, str) and ID.fullmatch(app_id) and app_id == path.stem,
                f"{path.name}: id must match the lowercase filename")
        require(type(app.get("enabled")) is bool, f"{app_id}: enabled must be true or false")
        require("scoop" in app or "homebrew" in app, f"{app_id}: no platforms configured")
        for platform in ("scoop", "homebrew"):
            if platform not in app:
                continue
            section = app[platform]
            require(isinstance(section, dict), f"{app_id}/{platform}: expected object")
            allowed = {"template", "assets"} | ({"kind"} if platform == "homebrew" else set())
            require(not (set(section) - allowed), f"{app_id}/{platform}: unknown keys")
            assets = section.get("assets", {})
            allowed_arches = {"64bit", "32bit", "arm64"} if platform == "scoop" else {"arm64", "x64", "universal"}
            require(isinstance(assets, dict) and assets and set(assets) <= allowed_arches,
                    f"{app_id}/{platform}: invalid assets/architectures")
            require("universal" not in assets or len(assets) == 1,
                    f"{app_id}: universal cannot be mixed with per-architecture files")
            names = []
            for pattern in assets.values():
                require(isinstance(pattern, str) and "{version}" in pattern,
                        f"{app_id}: asset filenames must contain {{version}}")
                name = pattern.replace("{version}", "1.2.3")
                require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name),
                        f"{app_id}: invalid asset filename {pattern!r}")
                names.append(name)
            require(len(names) == len(set(names)), f"{app_id}: duplicate asset patterns")
            template_name = section.get("template", "")
            require(isinstance(template_name, str) and template_name.startswith("templates/"),
                    f"{app_id}: templates must be under templates/")
            template_path = inside(root, template_name)
            require(template_path.is_file(), f"{app_id}: missing template {template_name}")
            if platform == "scoop":
                manifest = read_json(template_path)
                require(isinstance(manifest, dict), f"{app_id}: Scoop template must be an object")
                require(not ({"version", "url", "hash", "checkver", "autoupdate"} & set(manifest)),
                        f"{app_id}: version/download/update fields are generated, not template fields")
                for key in ("description", "homepage", "license"):
                    require(manifest.get(key), f"{app_id}: Scoop template needs {key}")
                overrides = manifest.get("architecture", {})
                require(isinstance(overrides, dict) and set(overrides) <= set(assets),
                        f"{app_id}: unexpected architecture overrides")
                for values in overrides.values():
                    require(isinstance(values, dict) and not ({"url", "hash"} & set(values)),
                            f"{app_id}: architecture URL/hash are generated")
            else:
                require(section.get("kind") in ("cask", "formula"),
                        f"{app_id}: Homebrew kind must be cask or formula")
                content = template_path.read_text(encoding="utf-8")
                tokens = set(PLACEHOLDER.findall(content))
                expected = {"VERSION", "REPOSITORY"}
                for arch in assets:
                    expected |= {f"URL_{arch.upper()}", f"SHA256_{arch.upper()}"}
                require("VERSION" in tokens and tokens <= expected,
                        f"{app_id}: missing VERSION or unsupported Homebrew placeholders")
                for arch in assets:
                    require({f"URL_{arch.upper()}", f"SHA256_{arch.upper()}"} <= tokens,
                            f"{app_id}: missing URL/SHA256 placeholders for {arch}")
                if section["kind"] == "cask":
                    require(re.search(r'^\s*cask "' + re.escape(app_id) + r'" do\s*$', content, re.M),
                            f"{app_id}: cask token must match app id")
                else:
                    class_name = "".join(part.capitalize() for part in app_id.split("-"))
                    require(f"class {class_name} < Formula" in content,
                            f"{app_id}: expected Formula class {class_name}")
                require(":no_check" not in content, f"{app_id}: a real SHA256 is required")
        apps.append(app)
    require(apps, "No app configurations found in apps/")
    return apps


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require(urlparse(newurl).scheme == "https", "Refusing an insecure redirect")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected and urlparse(newurl).hostname != urlparse(req.full_url).hostname:
            redirected.remove_header("Authorization")
        return redirected


class GitHub:
    def __init__(self, repository, token=None):
        require(REPOSITORY.fullmatch(repository), "Invalid owner/repository")
        self.repository = repository
        self.token = token
        self.opener = build_opener(SafeRedirect())

    def open(self, url, api=False):
        headers = {"User-Agent": "MyApps-release-sync/1"}
        if api:
            require(urlparse(url).hostname == "api.github.com", "Invalid API host")
            headers.update({"Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28"})
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
        for attempt in range(3):
            try:
                return self.opener.open(Request(url, headers=headers), timeout=90)
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise SyncError(f"HTTP {exc.code} fetching {url}") from exc
            except (URLError, TimeoutError) as exc:
                if attempt == 2:
                    raise SyncError(f"Download failed: {url}: {exc}") from exc
            time.sleep(2 ** attempt)
        raise SyncError(f"Cannot fetch {url}")

    def api(self, suffix):
        with self.open(f"https://api.github.com/repos/{self.repository}/{suffix}", api=True) as response:
            return json.load(response)

    def pages(self, suffix):
        page = 1
        while True:
            batch = self.api(f"{suffix}?per_page=100&page={page}")
            require(isinstance(batch, list), "Invalid paginated GitHub response")
            yield from batch
            if len(batch) < 100:
                break
            page += 1

    def releases(self):
        return list(self.pages("releases"))

    def release(self, tag):
        return self.api(f"releases/tags/{quote(tag, safe='')}")

    def assets(self, release):
        release_id = release.get("id")
        require(type(release_id) is int and release_id > 0, "Invalid Release id")
        return list(self.pages(f"releases/{release_id}/assets"))

    def checksum(self, asset):
        # Public release attachments: never send the API token to download hosts.
        digest = hashlib.sha256()
        size = 0
        with self.open(asset["browser_download_url"]) as response:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
                require(size <= asset["size"], "Downloaded attachment exceeds its declared size")
        require(size == asset["size"], "Downloaded attachment is incomplete")
        actual = digest.hexdigest()
        api_digest = asset.get("digest")
        if api_digest and api_digest.startswith("sha256:"):
            require(api_digest == f"sha256:{actual}", "Attachment does not match GitHub's SHA256")
        return actual


def release_version(app, release):
    if release.get("draft") or release.get("prerelease"):
        return None
    tag = release.get("tag_name", "")
    prefix = app["id"] + "-v"
    if not isinstance(tag, str) or not tag.startswith(prefix):
        return None
    version = tag[len(prefix):]
    return version if VERSION.fullmatch(version) else None


def fingerprint(asset, url, name):
    require(type(asset.get("id")) is int and asset["id"] > 0, f"Invalid asset id: {name}")
    require(type(asset.get("size")) is int and asset["size"] > 0, f"Empty or invalid asset: {name}")
    require(asset.get("state") == "uploaded", f"Asset is not fully uploaded: {name}")
    return {"name": name, "url": url, "id": asset["id"], "size": asset["size"],
            "updated_at": asset.get("updated_at"), "digest": asset.get("digest")}


def render(root, app, state):
    """Render both platforms without evaluating Ruby or application code."""
    changes = {}
    app_id = app["id"]
    if "scoop" in app:
        manifest = copy.deepcopy(read_json(inside(root, app["scoop"]["template"])))
        manifest["version"] = state["version"]
        architecture = manifest.setdefault("architecture", {})
        for arch in app["scoop"]["assets"]:
            artifact = state["assets"][f"scoop/{arch}"]
            architecture.setdefault(arch, {}).update(url=artifact["url"], hash=artifact["sha256"])
        changes[f"bucket/{app_id}.json"] = json_text(manifest)
    if "homebrew" in app:
        values = {"VERSION": state["version"], "REPOSITORY": state["repository"]}
        for arch in app["homebrew"]["assets"]:
            artifact = state["assets"][f"homebrew/{arch}"]
            values[f"URL_{arch.upper()}"] = artifact["url"]
            values[f"SHA256_{arch.upper()}"] = artifact["sha256"]
        template = inside(root, app["homebrew"]["template"]).read_text(encoding="utf-8")
        # Escape Ruby string interpolation, quotes and backslashes even though
        # GitHub repository, tag and attachment names are tightly validated.
        def substitute(match):
            value = values[match.group(1)]
            return value.replace("\\", "\\\\").replace('"', '\\"').replace("#{", r"\#{")
        content = PLACEHOLDER.sub(substitute, template)
        require("@@" not in content, f"{app_id}: unresolved Ruby placeholder")
        folder = "Casks" if app["homebrew"]["kind"] == "cask" else "Formula"
        changes[f"{folder}/{app_id}.rb"] = content.rstrip() + "\n"
    return changes


def make_plan(root, app, release, client):
    version = release_version(app, release)
    require(version, f"{app['id']}: not a supported stable release")
    app_id, tag = app["id"], release["tag_name"]
    state_path = inside(root, f".release-state/{app_id}.json")
    previous = read_json(state_path) if state_path.exists() else None
    if previous:
        require(previous["repository"] == client.repository,
                f"{app_id}: state belongs to a different repository; start a fresh template")
        if version_key(version) < version_key(previous["version"]):
            print(f"Skip old release {tag}; current version is {previous['version']}")
            return {}
    listed = client.assets(release)
    by_name = {}
    for asset in listed:
        name = asset.get("name")
        require(name not in by_name, f"Duplicate Release attachment: {name}")
        by_name[name] = asset
    selected = {}
    # Check every required attachment before downloading or modifying files.
    for platform in ("scoop", "homebrew"):
        for arch, pattern in app.get(platform, {}).get("assets", {}).items():
            name = pattern.replace("{version}", version)
            require(name in by_name, f"{tag}: required attachment missing: {name}")
            asset = by_name[name]
            expected_url = (f"https://github.com/{client.repository}/releases/download/"
                            f"{quote(tag, safe='')}/{quote(name, safe='')}")
            require(asset.get("browser_download_url") == expected_url,
                    f"{tag}: attachment URL is not in this repository: {name}")
            selected[f"{platform}/{arch}"] = (asset, fingerprint(asset, expected_url, name))
    same_version = previous and version_key(version) == version_key(previous["version"])
    if same_version:
        require(previous["version"] == version and previous["tag"] == tag,
                f"{tag}: equivalent version already published under another tag")
        old_fingerprints = {key: {k: v for k, v in item.items() if k != "sha256"}
                            for key, item in previous["assets"].items()}
        new_fingerprints = {key: item for key, (_, item) in selected.items()}
        require(old_fingerprints == new_fingerprints,
                f"{tag}: published attachments changed; publish a NEW version instead")
        state = previous
    else:
        assets = {}
        for key, (asset, metadata) in selected.items():
            checksum = client.checksum(asset)
            require(SHA256.fullmatch(checksum), f"{tag}: invalid SHA256")
            assets[key] = dict(metadata, sha256=checksum)
        state = {"schema_version": 1, "repository": client.repository, "id": app_id,
                 "tag": tag, "version": version, "assets": assets}
    plan = render(root, app, state)
    plan[f".release-state/{app_id}.json"] = json_text(state)
    return plan


def synchronize(root, client, tag=None, dry_run=False):
    apps = [app for app in load_apps(root) if app["enabled"]]
    releases = [client.release(tag)] if tag else client.releases()
    plan = {}
    matched = False
    for app in apps:
        candidates = [(release_version(app, release), release) for release in releases]
        candidates = [(version, release) for version, release in candidates if version]
        if not candidates:
            continue
        matched = True
        _, release = max(candidates, key=lambda pair: version_key(pair[0]))
        plan.update(make_plan(root, app, release, client))
    if tag and not matched:
        print(f"No enabled app matches a stable release at {tag}; nothing to update")
    changed = {name: content for name, content in plan.items()
               if not inside(root, name).exists() or
               inside(root, name).read_text(encoding="utf-8") != content}
    # All apps/platforms have validated and hashed before any output is written.
    for name, content in changed.items():
        print(f"{'Would update' if dry_run else 'Update'} {name}")
        if not dry_run:
            target = inside(root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            newline = "\r\n" if name.startswith("bucket/") and name.endswith(".json") else "\n"
            target.write_text(content, encoding="utf-8", newline=newline)
    return sorted(changed)


def validate_repository(root):
    apps = load_apps(root)
    states = set()
    for app in apps:
        state_path = inside(root, f".release-state/{app['id']}.json")
        if not state_path.exists():
            for folder, suffix in (("bucket", ".json"), ("Casks", ".rb"), ("Formula", ".rb")):
                require(not inside(root, f"{folder}/{app['id']}{suffix}").exists(),
                        f"{app['id']}: generated manifest has no release state")
            continue
        state = read_json(state_path)
        states.add(app["id"])
        require(state.get("schema_version") == 1 and state.get("id") == app["id"],
                f"{app['id']}: invalid release state")
        version_key(state["version"])
        require(REPOSITORY.fullmatch(state["repository"]), "Invalid state repository")
        require(state["tag"] == app["id"] + "-v" + state["version"], "Invalid state tag")
        expected_keys = {f"{p}/{a}" for p in ("scoop", "homebrew") for a in app.get(p, {}).get("assets", {})}
        require(set(state["assets"]) == expected_keys, f"{app['id']}: state architectures changed")
        for key, artifact in state["assets"].items():
            platform, arch = key.split("/")
            name = app[platform]["assets"][arch].replace("{version}", state["version"])
            url = (f"https://github.com/{state['repository']}/releases/download/"
                   f"{quote(state['tag'], safe='')}/{quote(name, safe='')}")
            require(artifact.get("name") == name and artifact.get("url") == url,
                    f"{app['id']}: invalid state attachment URL/name")
            require(isinstance(artifact.get("sha256"), str) and SHA256.fullmatch(artifact["sha256"]),
                    f"{app['id']}: invalid state SHA256")
        for name, expected in render(root, app, state).items():
            output = inside(root, name)
            require(output.exists() and output.read_text(encoding="utf-8") == expected,
                    f"{name}: output differs from template/state; run sync to regenerate")
    require({p.stem for p in (root / ".release-state").glob("*.json")} == states,
            "Orphan release states found; keep the associated app configurations")
    print(f"Validated {len(apps)} app configurations and {len(states)} published apps")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="Sync exactly one stable app-vX.Y.Z release")
    group.add_argument("--all", action="store_true", help="Reconcile all apps; paginate all releases")
    group.add_argument("--check", action="store_true", help="Offline configuration/output validation")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            validate_repository(ROOT)
            return 0
        require(args.repository, "--repository owner/repository is required")
        client = GitHub(args.repository, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
        changed = synchronize(ROOT, client, args.tag, args.dry_run)
        if not args.dry_run:
            validate_repository(ROOT)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                output.write(f"changed={'true' if changed else 'false'}\n")
        if not changed:
            print("Manifests already up to date")
        return 0
    except (SyncError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
