$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& (Join-Path $PSScriptRoot "lint.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$model = Join-Path $root "models\vosk-model-small-en-us-0.15"
if (-not (Test-Path (Join-Path $model "conf"))) {
    throw "The Vosk model is missing. Follow README.md before making a release."
}
$python = Join-Path $root ".venv\Scripts\python.exe"
& $python -m PyInstaller --noconfirm --clean --windowed --name PROVIDA `
    --distpath (Join-Path $root "dist\release-1.1.1") `
    --workpath (Join-Path $root "build\release-1.1.1") `
    --paths (Join-Path $root "src") `
    --add-data "$model;models\vosk-model-small-en-us-0.15" `
    --collect-all vosk `
    (Join-Path $root "src\provida\__main__.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
