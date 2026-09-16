$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$existing = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like "*$root\bridge.py*" }
if ($existing) { Write-Output 'X3 bridge is already running.'; exit 0 }
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run Setup.ps1 first to create the local Python environment.' }
$process = Start-Process -FilePath $python -ArgumentList @('-u', ('"' + $root + '\bridge.py"')) -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput "$root\bridge.log" -RedirectStandardError "$root\bridge-errors.log" -PassThru
Write-Output "X3 bridge started (PID $($process.Id)); waiting for the USB device if disconnected."
