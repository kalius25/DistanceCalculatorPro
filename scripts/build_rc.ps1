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

Write-Host "== DistanceCalculatorPro v1.3 RC2 build =="

Write-Host "== RC release metadata gate =="
Invoke-CheckedPython @(
    "-m", "app.release.rc_release_gate", "."
)

Write-Host "== Automated regression gate =="
Invoke-CheckedPython @(
    "-m", "pytest"
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

Write-Host "Build PASS: dist/DistanceCalculatorPro"
