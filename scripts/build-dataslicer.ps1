$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$specPath = Join-Path $repoRoot "packaging\pyinstaller\dataslicer.spec"
$exePath = Join-Path $repoRoot "dist\DataSlicer.exe"

Set-Location $repoRoot

Write-Host "Building DataSlicer.exe with PyInstaller..."
python -m PyInstaller $specPath --noconfirm --clean

if (-not (Test-Path $exePath)) {
    throw "Build finished, but $exePath was not created."
}

Write-Host "DataSlicer executable created:"
Write-Host $exePath

