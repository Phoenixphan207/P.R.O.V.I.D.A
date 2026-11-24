$ErrorActionPreference = "Stop"
$env:QT_QPA_PLATFORM = "offscreen"
$env:PROVIDA_DATA_DIR = Join-Path $env:TEMP "provida-tests"
$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
& $python -m pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
