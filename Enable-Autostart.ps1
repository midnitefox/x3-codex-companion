$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not (Test-Path "$root\.venv\Scripts\python.exe")) { throw 'Run Setup.ps1 first.' }
Get-Command node.exe -ErrorAction Stop | Out-Null
$linkPath = Join-Path ([Environment]::GetFolderPath('Startup')) 'X3 Codex Bridge.lnk'
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($linkPath)
if ((Test-Path -LiteralPath $linkPath) -and $link.Arguments -notlike "*$root\Watch-Codex.ps1*") {
    throw 'A different X3 bridge already owns the startup shortcut. Disable that installation first.'
}
$link.TargetPath = (Get-Process -Id $PID).Path
$link.Arguments = '-NoProfile -NonInteractive -WindowStyle Hidden -File "' + $root + '\Watch-Codex.ps1"'
$link.WorkingDirectory = $root
$link.WindowStyle = 7
$link.Description = 'Run the X3 status bridge while Codex desktop is open.'
$link.Save()
Start-Process -FilePath $link.TargetPath -ArgumentList $link.Arguments -WorkingDirectory $root -WindowStyle Hidden
Write-Output 'Codex lifecycle watcher enabled at Windows sign-in and started now.'
