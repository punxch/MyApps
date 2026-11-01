param(
    [Parameter(Mandatory = $true)][string]$ScoopRoot,
    [Parameter(Mandatory = $true)][string]$BucketRoot
)
$ErrorActionPreference = 'Stop'
$manifest = Join-Path $BucketRoot 'bucket/adb-status.json'
if (!(Test-Path -LiteralPath $manifest)) {
    Write-Output 'ADB Status is not published yet; skipping installation validation.'
    exit 0
}
$entry = Join-Path $ScoopRoot 'bin/scoop.ps1'
$env:SCOOP_HOME = $ScoopRoot
# Use the checked-out Scoop core as an isolated installation, without changing
# the runner user's existing Scoop installation or profile.
foreach ($folder in @('shims', 'cache', 'buckets', 'apps/scoop')) {
    New-Item -ItemType Directory -Force (Join-Path $env:SCOOP $folder) | Out-Null
}
New-Item -ItemType Junction -Path (Join-Path $env:SCOOP 'apps/scoop/current') -Target $ScoopRoot | Out-Null
$installed = $false
try {
    & $entry install $manifest --no-cache
    if ($LASTEXITCODE -ne 0) { throw 'Scoop installation failed.' }
    $installed = $true
    $executable = Join-Path $env:SCOOP 'apps/adb-status/current/ADB Status.exe'
    if (!(Test-Path -LiteralPath $executable)) { throw 'Installed executable missing.' }
    if (!(Test-Path -LiteralPath (Join-Path $env:SCOOP 'shims/adb-status.exe'))) {
        throw 'adb-status command shim missing.'
    }
    $shortcut = Join-Path $env:APPDATA 'Microsoft/Windows/Start Menu/Programs/Scoop Apps/ADB Status.lnk'
    if (!(Test-Path -LiteralPath $shortcut)) { throw 'Start menu shortcut missing.' }
    $shell = New-Object -ComObject WScript.Shell
    $target = $shell.CreateShortcut($shortcut).TargetPath
    if (!(Test-Path -LiteralPath $target) -or (Split-Path $target -Leaf) -ne 'ADB Status.exe') {
        throw 'Start menu shortcut points to the wrong application.'
    }
    $bytes = [IO.File]::ReadAllBytes($executable)
    $pe = [BitConverter]::ToInt32($bytes, 0x3c)
    if ([BitConverter]::ToUInt32($bytes, $pe) -ne 0x4550 -or
        [BitConverter]::ToUInt16($bytes, $pe + 4) -ne 0x8664 -or
        [BitConverter]::ToUInt16($bytes, $pe + 24 + 68) -ne 2) {
        throw 'Expected an x64 Windows GUI executable.'
    }
    Write-Output 'Scoop download, checksum, installation, command shim, shortcut and x64 GUI executable validated.'
} finally {
    if ($installed) {
        & $entry uninstall adb-status
        if ($LASTEXITCODE -ne 0) { throw 'Scoop uninstall failed.' }
        if (Test-Path -LiteralPath (Join-Path $env:SCOOP 'apps/adb-status/current/ADB Status.exe')) {
            throw 'Scoop uninstall left the current executable installed.'
        }
        Write-Output 'Scoop uninstallation validated.'
    }
}
