#!/usr/bin/env python3
"""Set repository links before publishing the first release."""
import argparse
from pathlib import Path
import sys

from sync_releases import REPOSITORY, SyncError, require

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOSITORY = "punxch/MyApps"


def configure(root, repository):
    require(REPOSITORY.fullmatch(repository), "Expected owner/repository")
    require(not list((root / ".release-state").glob("*.json")),
            "This repository has published state; initialization cannot migrate existing releases")
    candidates = [root / "README.md", root / "bin" / "auto-pr.ps1"]
    candidates += sorted((root / "docs").glob("*.md"))
    candidates += sorted((root / "templates").glob("*.json"))
    changed = []
    for path in candidates:
        content = path.read_text(encoding="utf-8")
        updated = content.replace(DEFAULT_REPOSITORY, repository)
        updated = updated.replace(DEFAULT_REPOSITORY.lower(), repository.lower())
        if content != updated:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(root).as_posix())
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository")
    args = parser.parse_args()
    try:
        changed = configure(ROOT, args.repository)
        print("Updated: " + ", ".join(changed) if changed else "Repository links already configured")
        return 0
    except (SyncError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
