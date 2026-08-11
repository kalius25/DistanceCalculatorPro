$ErrorActionPreference = "Stop"

function Invoke-CheckedPython {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE"
    }
}

Write-Host "== DistanceCalculatorPro RC build =="

Invoke-CheckedPython @(
    "-m", "pip", "install", "--upgrade", "pyinstaller"
)
Invoke-CheckedPython @(
    "-m", "PyInstaller", "--noconfirm", "--clean",
    "DistanceCalculatorPro.spec"
)

Write-Host "== Packaging smoke =="
Invoke-CheckedPython @(
    "-m", "app.release.package_smoke",
    "dist/DistanceCalculatorPro"
)

Write-Host "== Executable startup/shutdown smoke =="
Invoke-CheckedPython @(
    "-m", "app.release.executable_smoke",
    "dist/DistanceCalculatorPro/DistanceCalculatorPro.exe"
)

Write-Host "Build PASS: dist/DistanceCalculatorPro"
