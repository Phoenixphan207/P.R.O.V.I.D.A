$ErrorActionPreference = "Stop"
$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
& $python -m ruff check src tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python -m compileall -q src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
