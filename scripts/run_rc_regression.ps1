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

Write-Host "== DistanceCalculatorPro v1.3 RC2 live regression =="

Write-Host "== Source quality gate =="
Invoke-CheckedPython @("-m", "pytest")

Write-Host "== Multi-provider GUI regression =="
Invoke-CheckedPython @(
    "-m",
    "scripts.smoke_multi_provider_gui_acceptance"
)

Write-Host "RC2 live regression: PASS"
