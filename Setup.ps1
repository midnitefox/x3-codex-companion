$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
Get-Command node.exe -ErrorAction Stop | Out-Null
$python = (Get-Command python.exe -ErrorAction Stop).Source
if (-not (Test-Path "$root\.venv\Scripts\python.exe")) {
    & $python -m venv "$root\.venv"
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
}
& "$root\.venv\Scripts\python.exe" -m pip install -r "$root\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Output 'Setup complete. First run .venv\Scripts\python.exe bridge.py --preview-only to check the feed.'
