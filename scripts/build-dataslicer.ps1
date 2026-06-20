$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$specPath = Join-Path $repoRoot "packaging\pyinstaller\dataslicer.spec"
$exePath = Join-Path $repoRoot "dist\DataSlicer.exe"
$sourcePath = Join-Path $repoRoot "src"
$webAssetsPath = Join-Path $repoRoot "src\gt_dataslicer\ui\web"

Set-Location $repoRoot

Write-Host "Building DataSlicer.exe with PyInstaller..."

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$uvCommand = Get-Command uv -ErrorAction SilentlyContinue

function Get-RunningDataSlicerBuildProcesses {
    if (-not (Test-Path $exePath)) {
        return @()
    }

    $targetPath = [System.IO.Path]::GetFullPath($exePath)
    return @(
        Get-CimInstance Win32_Process -Filter "Name = 'DataSlicer.exe'" |
            Where-Object {
                $_.ExecutablePath -and
                ([System.IO.Path]::GetFullPath($_.ExecutablePath) -ieq $targetPath)
            }
    )
}

function Assert-DataSlicerExecutableIsNotRunning {
    $runningProcesses = @(Get-RunningDataSlicerBuildProcesses)
    if ($runningProcesses.Count -eq 0) {
        return
    }

    $processIds = ($runningProcesses | ForEach-Object { $_.ProcessId }) -join ", "
    throw "DataSlicer.exe is currently running from $exePath (PID(s): $processIds). Close DataSlicer and run this script again."
}

function Set-LocalSourceFirstOnPythonPath {
    $pathParts = @(
        [System.IO.Path]::GetFullPath($sourcePath),
        [System.IO.Path]::GetFullPath($repoRoot)
    )
    if ($env:PYTHONPATH) {
        $pathParts += $env:PYTHONPATH
    }
    $env:PYTHONPATH = $pathParts -join [System.IO.Path]::PathSeparator
}

function Remove-PreviousExecutable {
    if (-not (Test-Path $exePath)) {
        return
    }

    $repoRootPath = [System.IO.Path]::GetFullPath($repoRoot)
    $targetPath = [System.IO.Path]::GetFullPath($exePath)
    if (-not $targetPath.StartsWith($repoRootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove executable outside repository: $targetPath"
    }

    Remove-Item -LiteralPath $exePath -Force
}

function Invoke-PythonBuild {
    try {
        & python -m PyInstaller $specPath --noconfirm --clean
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        Write-Warning "python failed to run the PyInstaller build. Exit code: $LASTEXITCODE"
        return $false
    }
    catch {
        Write-Warning "python failed to run the PyInstaller build. $($_.Exception.Message)"
        return $false
    }
}

function Invoke-UvBuild {
    try {
        & uv run --extra freeze python -m PyInstaller $specPath --noconfirm --clean
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        Write-Warning "uv failed to run the PyInstaller build. Exit code: $LASTEXITCODE"
        return $false
    }
    catch {
        Write-Warning "uv failed to run the PyInstaller build. $($_.Exception.Message)"
        return $false
    }
}

function Get-UiAssetValidationScript {
    return @'
from hashlib import sha256
from pathlib import Path
import sys

from PyInstaller.archive.readers import CArchiveReader

exe_path = Path(sys.argv[1])
web_assets_path = Path(sys.argv[2])
required_assets = {
    "index.html": ["cleanBase", "cleanThenSummarization", "summarizationOnly", "summarizationGroupByInput", "summarizationTotalsInput"],
    "app.js": ["summarization_group_by", "summarization_totals", "bindEnterFlow"],
    "styles.css": [],
}

archive = CArchiveReader(str(exe_path))

def extract_asset(relative_name: str) -> bytes:
    archive_name = f"gt_dataslicer/ui/web/{relative_name}"
    for candidate in (archive_name, archive_name.replace("/", "\\")):
        if candidate in archive.toc:
            return archive.extract(candidate)
    raise SystemExit(f"Missing UI asset in executable: {archive_name}")

for relative_name, markers in required_assets.items():
    source_bytes = (web_assets_path / relative_name).read_bytes()
    bundled_bytes = extract_asset(relative_name)
    if sha256(source_bytes).hexdigest() != sha256(bundled_bytes).hexdigest():
        raise SystemExit(f"Bundled UI asset is stale or different: {relative_name}")
    bundled_text = bundled_bytes.decode("utf-8", errors="replace")
    missing_markers = [marker for marker in markers if marker not in bundled_text]
    if missing_markers:
        raise SystemExit(f"Bundled UI asset {relative_name} is missing markers: {', '.join(missing_markers)}")

print("Validated bundled UI assets: index.html, app.js, and styles.css match src/gt_dataslicer/ui/web.")
'@
}

function Test-BuiltExecutableContainsCurrentUiAssetsWithPython {
    try {
        $output = Get-UiAssetValidationScript | python - $exePath $webAssetsPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            $output | ForEach-Object { Write-Host $_ }
            return $true
        }
        $output | ForEach-Object { Write-Warning $_ }
        return $false
    }
    catch {
        Write-Warning "python failed to validate bundled UI assets. $($_.Exception.Message)"
        return $false
    }
}

function Test-BuiltExecutableContainsCurrentUiAssetsWithUv {
    try {
        $output = Get-UiAssetValidationScript | uv run --extra freeze python - $exePath $webAssetsPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            $output | ForEach-Object { Write-Host $_ }
            return $true
        }
        $output | ForEach-Object { Write-Warning $_ }
        return $false
    }
    catch {
        Write-Warning "uv failed to validate bundled UI assets. $($_.Exception.Message)"
        return $false
    }
}

function Assert-BuiltExecutableContainsCurrentUiAssets {
    if ($pythonCommand -and (Test-BuiltExecutableContainsCurrentUiAssetsWithPython)) {
        return
    }
    if ($uvCommand -and (Test-BuiltExecutableContainsCurrentUiAssetsWithUv)) {
        return
    }

    throw "DataSlicer.exe was created, but its bundled UI assets could not be verified. Rebuild failed to prevent shipping a stale interface."
}

$buildSucceeded = $false

Set-LocalSourceFirstOnPythonPath
Assert-DataSlicerExecutableIsNotRunning
Remove-PreviousExecutable

if ($pythonCommand) {
    $buildSucceeded = Invoke-PythonBuild
    if (-not $buildSucceeded -and $uvCommand) {
        Write-Host "Falling back to uv..."
    }
}

if (-not $buildSucceeded -and $uvCommand) {
    $buildSucceeded = Invoke-UvBuild
}

if (-not $pythonCommand -and -not $uvCommand) {
    throw "Python 3.12+ or uv is required to build DataSlicer.exe. Install Python or uv and run this script again."
}

if (-not $buildSucceeded) {
    Assert-DataSlicerExecutableIsNotRunning
    throw "DataSlicer.exe build failed. Install the freeze dependencies for Python or use uv with the freeze extra, then run this script again."
}

if (-not (Test-Path $exePath)) {
    throw "Build finished, but $exePath was not created."
}

Assert-BuiltExecutableContainsCurrentUiAssets

Write-Host "DataSlicer executable created:"
Write-Host $exePath
