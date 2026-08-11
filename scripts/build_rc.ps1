$ErrorActionPreference = "Stop"

Write-Host "== DistanceCalculatorPro RC build =="

python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --clean DistanceCalculatorPro.spec

Write-Host "== Packaging smoke =="
python -m app.release.package_smoke dist/DistanceCalculatorPro

Write-Host "Build PASS: dist/DistanceCalculatorPro"
