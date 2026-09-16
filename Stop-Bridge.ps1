$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$bridges = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like "*$root\bridge.py*" }
foreach ($bridge in $bridges) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $($bridge.ProcessId)" | Where-Object { $_.Name -eq 'node.exe' -and $_.CommandLine -like '*status-source.cjs*' }
    $children | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }
    Stop-Process -Id $bridge.ProcessId -ErrorAction SilentlyContinue
}
Write-Output 'X3 bridge stopped.'
