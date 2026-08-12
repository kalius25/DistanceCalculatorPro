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

Write-Host "== DistanceCalculatorPro Stable build =="

Write-Host "== Stable release metadata gate =="
Invoke-CheckedPython @(
    "-m", "app.release.stable_release_gate", "."
)

Invoke-CheckedPython @(
    "-m", "pip", "install", "--upgrade", "pyinstaller"
)

Write-Host "== Ensure Playwright Chromium =="
Invoke-CheckedPython @(
    "-m", "playwright", "install", "chromium"
)

Write-Host "== Stage bundled Chromium =="
Invoke-CheckedPython @(
    "-m", "app.release.stage_browser",
    "build/bundled-browser/chromium"
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

Write-Host "Stable Build PASS: dist/DistanceCalculatorPro"
