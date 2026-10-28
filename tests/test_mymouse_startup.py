import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt", "Windows installer hook")
class MyMouseStartupTests(unittest.TestCase):
    def run_hook(self, value, directory=r"D:\Scoop\apps\mymouse\0.1.2"):
        template = json.loads((ROOT / "templates/mymouse.scoop.json").read_text())
        manifest = json.loads((ROOT / "bucket/mymouse.json").read_text())
        self.assertEqual(template.get("post_install", []), manifest.get("post_install", []))
        # Execute the actual Scoop hook with the same dynamically scoped $dir.
        # Registry commands are replaced; tests never touch the user's Run key.
        script = r'''
param($InputFile)
$ErrorActionPreference = 'Stop'
$inputData = Get-Content -LiteralPath $InputFile -Raw | ConvertFrom-Json
$dir = $inputData.directory
$script:startupValue = $inputData.value
$script:writes = 0
function Get-ItemProperty {
    param($LiteralPath, $Name, $ErrorAction)
    if ($LiteralPath -ne 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -or $Name -ne 'MyMouse') { throw 'unexpected registry read' }
    return @{ MyMouse = $script:startupValue }
}
function Set-ItemProperty {
    param($LiteralPath, $Name, $Value, $ErrorAction)
    if ($LiteralPath -ne 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -or $Name -ne 'MyMouse') { throw 'unexpected registry write' }
    $script:startupValue = $Value
    $script:writes += 1
}
Invoke-Command ([scriptblock]::Create($inputData.hook -join "`r`n"))
@{value = $script:startupValue; writes = $script:writes} | ConvertTo-Json -Compress
'''
        with tempfile.TemporaryDirectory() as directory_path:
            path = Path(directory_path)
            (path / "run.ps1").write_text(script, encoding="utf-8")
            (path / "input.json").write_text(json.dumps({
                "directory": directory, "value": value, "hook": template.get("post_install", []),
            }), encoding="utf-8")
            process = subprocess.run([
                "pwsh", "-NoProfile", "-NonInteractive", "-File", str(path / "run.ps1"),
                str(path / "input.json"),
            ], capture_output=True, text=True, encoding="utf-8", timeout=20)
            self.assertEqual(process.returncode, 0, process.stderr)
            return json.loads(process.stdout)

    def test_upgrade_repairs_old_version_without_opening_desktop(self):
        value = r'"D:\Scoop\apps\mymouse\0.1.0\mymouse.exe" --data-dir "C:\My Profile\config" daemon run'
        result = self.run_hook(value)
        self.assertEqual(result["value"], r'"D:\Scoop\apps\mymouse\current\mymouse.exe" --background --data-dir "C:\My Profile\config" daemon run')
        self.assertEqual(result["writes"], 1)
        repeated = self.run_hook(result["value"])
        self.assertEqual(repeated["value"], result["value"])
        self.assertEqual(self.run_hook(value, r"D:\Scoop\apps\mymouse\current")["value"], result["value"])

    def test_disabled_startup_stays_disabled(self):
        result = self.run_hook(None)
        self.assertIsNone(result["value"])
        self.assertEqual(result["writes"], 0)

    def test_other_installation_and_custom_commands_are_preserved(self):
        for value in [
            r'"E:\Other\mymouse\0.1.0\mymouse.exe" --data-dir "C:\profile" daemon run',
            r'"D:\Scoop\apps\mymouse\0.1.0\mymouse.exe" --custom-option',
        ]:
            with self.subTest(value=value):
                self.assertEqual(self.run_hook(value), {"value": value, "writes": 0})

    def test_existing_background_flag_is_not_duplicated(self):
        value = r'"D:\Scoop\apps\mymouse\0.1.1\mymouse.exe" --background --data-dir "C:\profile" daemon run'
        result = self.run_hook(value)
        self.assertEqual(result["value"].count("--background"), 1)
        self.assertIn(r'\current\mymouse.exe"', result["value"])
