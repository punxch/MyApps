import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT / "scripts"))
import sync_releases as sync

REPOSITORY = "punxch/MyApps"


def project(root):
    for folder in ("apps", "templates"):
        shutil.copytree(FIXTURES / folder, root / folder)
    for path in (root / "apps").glob("*.json"):
        value = sync.read_json(path)
        value["enabled"] = True
        path.write_text(sync.json_text(value), encoding="utf-8")
    return root


def release(app_id="alpha", version="1.2.0", root=FIXTURES, **extra):
    config = sync.read_json(root / "apps" / f"{app_id}.json")
    tag = app_id + "-v" + version
    value = {"id": int(hashlib.sha256(tag.encode()).hexdigest()[:8], 16),
             "tag_name": tag, "draft": False, "prerelease": False, "assets": []}
    for platform in ("scoop", "homebrew"):
        for pattern in config.get(platform, {}).get("assets", {}).values():
            name = pattern.replace("{version}", version)
            data = ("test fixture only: " + name).encode()
            value["assets"].append({
                "id": int(hashlib.sha256(name.encode()).hexdigest()[:8], 16),
                "name": name, "size": len(data), "state": "uploaded",
                "updated_at": "2026-01-01T00:00:00Z",
                "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
                "browser_download_url": f"https://github.com/{REPOSITORY}/releases/download/{tag}/{name}"
            })
    value.update(extra)
    return value


class FakeGitHub:
    repository = REPOSITORY

    def __init__(self, releases):
        self.data = copy.deepcopy(releases)
        self.downloads = 0

    def releases(self):
        return self.data

    def release(self, tag):
        return next(item for item in self.data if item["tag_name"] == tag)

    def assets(self, release):
        return release["assets"]

    def checksum(self, asset):
        self.downloads += 1
        return hashlib.sha256(("test fixture only: " + asset["name"]).encode()).hexdigest()
