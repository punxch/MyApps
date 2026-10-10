import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import Request

from support import ROOT, REPOSITORY, FakeGitHub, project, release, sync


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = project(Path(self.temp.name))

    def read(self, name):
        return sync.read_json(self.root / name)

    def config(self, app_id, change):
        path = self.root / "apps" / f"{app_id}.json"
        value = sync.read_json(path)
        change(value)
        path.write_text(sync.json_text(value), encoding="utf-8")

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_two_apps_both_platforms_and_checksums(self):
        client = FakeGitHub([release(), release("beta", "3.4.0")])
        files = sync.synchronize(self.root, client)
        self.assertEqual(len(files), 6)
        alpha = self.read("bucket/alpha.json")
        self.assertEqual(alpha["version"], "1.2.0")
        artifact = client.data[0]["assets"][0]
        self.assertEqual(alpha["architecture"]["64bit"]["hash"], artifact["digest"][7:])
        self.assertIn("/alpha-v1.2.0/", alpha["architecture"]["64bit"]["url"])
        self.assertIn('app "Alpha.app"', (self.root / "Casks/alpha.rb").read_text())
        self.assertIn('version "3.4.0"', (self.root / "Formula/beta.rb").read_text())
        sync.validate_repository(self.root)

    def test_tag_updates_only_matching_app(self):
        client = FakeGitHub([release(), release("beta")])
        sync.synchronize(self.root, client, tag="alpha-v1.2.0")
        self.assertTrue((self.root / "bucket/alpha.json").exists())
        self.assertFalse((self.root / "bucket/beta.json").exists())

    def test_identical_run_is_noop_without_redownloading(self):
        client = FakeGitHub([release()])
        sync.synchronize(self.root, client)
        snapshot = self.snapshot()
        client.downloads = 0
        self.assertEqual(sync.synchronize(self.root, client), [])
        self.assertEqual(client.downloads, 0)
        self.assertEqual(self.snapshot(), snapshot)

    def test_missing_mac_asset_does_not_write_windows_manifest(self):
        item = release()
        item["assets"].pop()
        snapshot = self.snapshot()
        with self.assertRaisesRegex(sync.SyncError, "required attachment missing"):
            sync.synchronize(self.root, FakeGitHub([item]))
        self.assertEqual(self.snapshot(), snapshot)

    def test_later_app_failure_does_not_write_earlier_app(self):
        bad = release("beta")
        bad["assets"].pop()
        snapshot = self.snapshot()
        with self.assertRaises(sync.SyncError):
            sync.synchronize(self.root, FakeGitHub([release(), bad]))
        self.assertEqual(self.snapshot(), snapshot)

    def test_failed_upgrade_preserves_both_previous_manifests(self):
        sync.synchronize(self.root, FakeGitHub([release()]))
        snapshot = self.snapshot()
        item = release(version="1.3.0")
        item["assets"] = item["assets"][:1]
        with self.assertRaises(sync.SyncError):
            sync.synchronize(self.root, FakeGitHub([item]))
        self.assertEqual(self.snapshot(), snapshot)

    def test_highest_numeric_version_not_list_order_or_global_latest(self):
        client = FakeGitHub([release(version="1.9.0"), release("beta", "99.0.0"),
                            release(version="1.10.0"), release(version="1.1.0")])
        sync.synchronize(self.root, client)
        self.assertEqual(self.read("bucket/alpha.json")["version"], "1.10.0")

    def test_old_release_cannot_downgrade(self):
        sync.synchronize(self.root, FakeGitHub([release(version="2.0.0")]))
        snapshot = self.snapshot()
        self.assertEqual(sync.synchronize(self.root, FakeGitHub([release()])), [])
        self.assertEqual(self.snapshot(), snapshot)

    def test_drafts_prereleases_and_unknown_tags_are_ignored(self):
        data = [release(version="2.0.0", draft=True),
                release(version="3.0.0", prerelease=True),
                release(tag_name="unrelated-v9.0.0"), release()]
        sync.synchronize(self.root, FakeGitHub(data))
        self.assertEqual(self.read("bucket/alpha.json")["version"], "1.2.0")

    def test_disabled_app_is_not_published(self):
        self.config("alpha", lambda c: c.update(enabled=False))
        self.assertEqual(sync.synchronize(self.root, FakeGitHub([release()])), [])
        self.assertFalse((self.root / "Casks/alpha.rb").exists())

    def test_unknown_single_tag_is_noop(self):
        self.assertEqual(sync.synchronize(self.root, FakeGitHub([release(tag_name="docs-v1.0.0")]),
                                          tag="docs-v1.0.0"), [])

    def test_same_version_replaced_attachment_is_rejected(self):
        sync.synchronize(self.root, FakeGitHub([release()]))
        snapshot = self.snapshot()
        replaced = release()
        replaced["assets"][0]["id"] += 1
        with self.assertRaisesRegex(sync.SyncError, "NEW version"):
            sync.synchronize(self.root, FakeGitHub([replaced]))
        self.assertEqual(self.snapshot(), snapshot)

    def test_dry_run_has_no_file_writes(self):
        snapshot = self.snapshot()
        self.assertEqual(len(sync.synchronize(self.root, FakeGitHub([release()]), dry_run=True)), 3)
        self.assertEqual(self.snapshot(), snapshot)

    def test_template_install_rules_preserved(self):
        path = self.root / "templates/alpha.scoop.json"
        value = sync.read_json(path)
        value.update(persist="data", pre_install="New-Item -ItemType Directory -Force \"$persist_dir/data\"")
        value["architecture"] = {"64bit": {"extract_dir": "Alpha"}}
        path.write_text(sync.json_text(value), encoding="utf-8")
        sync.synchronize(self.root, FakeGitHub([release()]))
        actual = self.read("bucket/alpha.json")
        self.assertEqual(actual["persist"], "data")
        self.assertEqual(actual["architecture"]["64bit"]["extract_dir"], "Alpha")

    def test_single_platform_supported(self):
        self.config("alpha", lambda c: c.pop("homebrew"))
        sync.synchronize(self.root, FakeGitHub([release()]))
        self.assertTrue((self.root / "bucket/alpha.json").exists())
        self.assertFalse((self.root / "Casks/alpha.rb").exists())

    def test_universal_cask_supported(self):
        self.config("alpha", lambda c: c["homebrew"].update(
            assets={"universal": "alpha-{version}-macos-universal.dmg"}))
        path = self.root / "templates/alpha.cask.rb"
        path.write_text('cask "alpha" do\n  version "@@VERSION@@"\n'
                        '  sha256 "@@SHA256_UNIVERSAL@@"\n  url "@@URL_UNIVERSAL@@"\n'
                        '  app "Alpha.app"\nend\n', encoding="utf-8")
        sync.synchronize(self.root, FakeGitHub([release(root=self.root)]))
        self.assertIn("universal.dmg", (self.root / "Casks/alpha.rb").read_text())

    def test_template_path_traversal_rejected(self):
        self.config("alpha", lambda c: c["scoop"].update(template="templates/../../escape.json"))
        with self.assertRaisesRegex(sync.SyncError, "escapes"):
            sync.load_apps(self.root)

    def test_unknown_config_field_rejected(self):
        self.config("alpha", lambda c: c.update(enabeld=True))
        with self.assertRaisesRegex(sync.SyncError, "unknown"):
            sync.load_apps(self.root)

    def test_missing_homebrew_checksum_placeholder_rejected(self):
        path = self.root / "templates/alpha.cask.rb"
        path.write_text(path.read_text().replace("@@SHA256_ARM64@@", "abc"), encoding="utf-8")
        with self.assertRaisesRegex(sync.SyncError, "missing URL/SHA256"):
            sync.load_apps(self.root)

    def test_untrusted_download_url_rejected_without_writes(self):
        item = release()
        item["assets"][0]["browser_download_url"] = "https://example.com/bad.zip"
        with self.assertRaisesRegex(sync.SyncError, "not in this repository"):
            sync.synchronize(self.root, FakeGitHub([item]))
        self.assertFalse((self.root / "bucket/alpha.json").exists())

    def test_changed_generated_output_detected(self):
        sync.synchronize(self.root, FakeGitHub([release()]))
        (self.root / "Casks/alpha.rb").write_text("broken\n")
        with self.assertRaisesRegex(sync.SyncError, "differs"):
            sync.validate_repository(self.root)

    def test_ruby_parser_when_available(self):
        if not shutil.which("ruby"):
            self.skipTest("Ruby is unavailable here; macOS/Ubuntu CI parses generated Ruby")
        sync.synchronize(self.root, FakeGitHub([release(), release("beta")]))
        for folder in ("Casks", "Formula"):
            for path in (self.root / folder).glob("*.rb"):
                subprocess.run(["ruby", "-c", str(path)], check=True, capture_output=True)


class GitHubTests(unittest.TestCase):
    def test_release_pagination_beyond_one_hundred(self):
        github = sync.GitHub(REPOSITORY)
        with patch.object(github, "api", side_effect=[list(range(100)), [100]]) as api:
            self.assertEqual(len(github.releases()), 101)
            self.assertIn("page=2", api.call_args.args[0])

    def test_asset_pagination(self):
        github = sync.GitHub(REPOSITORY)
        with patch.object(github, "api", side_effect=[list(range(100)), [100]]):
            self.assertEqual(len(github.assets({"id": 42})), 101)

    def test_checksum_is_computed_from_downloaded_bytes(self):
        client = sync.GitHub(REPOSITORY, token="not-a-real-token")
        asset = release()["assets"][0]
        data = ("test fixture only: " + asset["name"]).encode()
        with patch.object(client, "open", return_value=io.BytesIO(data)) as download:
            self.assertEqual(client.checksum(asset), hashlib.sha256(data).hexdigest())
            self.assertEqual(download.call_args.kwargs, {})  # never api=True

    def test_truncated_download_is_rejected(self):
        client = sync.GitHub(REPOSITORY)
        with patch.object(client, "open", return_value=io.BytesIO(b"x")):
            with self.assertRaisesRegex(sync.SyncError, "incomplete"):
                client.checksum(release()["assets"][0])

    def test_api_digest_mismatch_is_rejected(self):
        client = sync.GitHub(REPOSITORY)
        asset = release()["assets"][0]
        asset["digest"] = "sha256:" + "0" * 64
        data = ("test fixture only: " + asset["name"]).encode()
        with patch.object(client, "open", return_value=io.BytesIO(data)):
            with self.assertRaisesRegex(sync.SyncError, "GitHub's SHA256"):
                client.checksum(asset)

    def test_redirect_does_not_forward_authorization(self):
        handler = sync.SafeRedirect()
        request = Request("https://api.github.com/foo", headers={"Authorization": "Bearer test"})
        redirected = handler.redirect_request(request, None, 302, "Found", {},
                                              "https://example.com/asset")
        self.assertIsNone(redirected.get_header("Authorization"))

    def test_redirect_to_http_rejected(self):
        with self.assertRaisesRegex(sync.SyncError, "insecure"):
            sync.SafeRedirect().redirect_request(Request("https://github.com/foo"), None,
                                                 302, "Found", {}, "http://example.com/asset")

    def test_invalid_versions_rejected(self):
        for version in ("1.2", "v1.2.3", "1.2.3-rc.1", "01.2.3", "1.2.3/../../x", "1.2.3３"):
            with self.subTest(version=version), self.assertRaises(sync.SyncError):
                sync.version_key(version)


if __name__ == "__main__":
    unittest.main()
