$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$specPath = Join-Path $repoRoot "packaging\pyinstaller\dataslicer.spec"
$exePath = Join-Path $repoRoot "dist\DataSlicer.exe"

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

$buildSucceeded = $false

Assert-DataSlicerExecutableIsNotRunning

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

Write-Host "DataSlicer executable created:"
Write-Host $exePath
