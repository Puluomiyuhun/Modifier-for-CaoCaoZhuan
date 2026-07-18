$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$buildTemp = $env:BANSHOU_BUILD_TEMP
if ([string]::IsNullOrWhiteSpace($buildTemp)) {
    $buildTemp = Join-Path $PSScriptRoot "build-temp"
}
$buildTemp = [System.IO.Path]::GetFullPath($buildTemp)
New-Item -ItemType Directory -Path $buildTemp -Force | Out-Null
$env:TEMP = $buildTemp
$env:TMP = $buildTemp
$env:PIP_CACHE_DIR = Join-Path $buildTemp "pip-cache"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $buildTemp "pyinstaller-cache"
Write-Host "Build temporary directory: $buildTemp"

function Assert-LastExitCode([string] $Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

python -c "import struct,sys; sys.exit(0 if struct.calcsize('P') == 4 else 1)"
Assert-LastExitCode "32-bit Python check"

python -m pip install -r requirements-dev-32.txt
Assert-LastExitCode "Dependency installation"

python -m py_compile main.py mywindow.py hook.py engine_profile.py process_memory.py capability_evidence.py evidence_collector.py
Assert-LastExitCode "Syntax compilation"

$previousQpaPlatform = $env:QT_QPA_PLATFORM
try {
    $env:QT_QPA_PLATFORM = "offscreen"
    python -m unittest discover -s tests -q
    Assert-LastExitCode "Test suite"
}
finally {
    $env:QT_QPA_PLATFORM = $previousQpaPlatform
}

python -m PyInstaller --noconfirm --clean banshou66.spec
Assert-LastExitCode "PyInstaller build"

$artifacts = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot "dist") -Filter "*.exe")
if ($artifacts.Count -ne 1) {
    throw "Expected exactly one release executable, found $($artifacts.Count)"
}

$artifact = $artifacts[0]
$digest = (Get-FileHash -LiteralPath $artifact.FullName -Algorithm SHA256).Hash
$checksumPath = "$($artifact.FullName).sha256"
[System.IO.File]::WriteAllText(
    $checksumPath,
    "$digest *$($artifact.Name)`r`n",
    [System.Text.UTF8Encoding]::new($false))

Write-Host "Build complete: $($artifact.FullName)"
Write-Host "SHA256: $digest"
