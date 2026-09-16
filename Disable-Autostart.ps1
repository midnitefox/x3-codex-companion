$ErrorActionPreference = 'Stop'
$linkPath = Join-Path ([Environment]::GetFolderPath('Startup')) 'X3 Codex Bridge.lnk'
if (Test-Path -LiteralPath $linkPath) {
    $link = (New-Object -ComObject WScript.Shell).CreateShortcut($linkPath)
    if ($link.Arguments -notlike "*$PSScriptRoot\Watch-Codex.ps1*") { throw 'Shortcut target changed; not removing it.' }
    Remove-Item -LiteralPath $linkPath
}
Get-CimInstance Win32_Process -Filter "name = 'pwsh.exe' OR name = 'powershell.exe'" |
    Where-Object { $_.CommandLine -like "*$PSScriptRoot\Watch-Codex.ps1*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId }
& "$PSScriptRoot\Stop-Bridge.ps1"
Write-Output 'Automatic X3 bridge startup disabled.'
