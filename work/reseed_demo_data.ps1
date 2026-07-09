$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$dbPath = Join-Path $repoRoot "data\adtech_demo.db"

if (Test-Path $dbPath) {
    Remove-Item -LiteralPath $dbPath
}

Write-Host "Demo database reset. Restart the API to regenerate seeded demo data."
