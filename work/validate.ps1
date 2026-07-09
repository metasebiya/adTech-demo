$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Virtual environment Python not found at $pythonExe"
}

Push-Location $repoRoot
try {
    & $pythonExe -m compileall apps
    & $pythonExe -m pytest -q
}
finally {
    Pop-Location
}
