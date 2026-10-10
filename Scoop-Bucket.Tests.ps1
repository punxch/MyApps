if (!$env:SCOOP_HOME) { $env:SCOOP_HOME = Resolve-Path (scoop prefix scoop) }
# Limit Scoop's Windows file-style checks to its own directory.
. "$env:SCOOP_HOME\test\Import-Bucket-Tests.ps1" -BucketPath "$PSScriptRoot/bucket"
