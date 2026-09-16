$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Bridge-Lifecycle.ps1"
$mutex = [Threading.Mutex]::new($false, 'Local\X3-Codex-Companion-Lifecycle')
$ownsMutex = $false
try {
    try { $ownsMutex = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $ownsMutex = $true }
    if (-not $ownsMutex) { exit 0 }
    $previous = $null
    while ($true) {
        try {
            $processes = @(Get-CimInstance Win32_Process -Filter "name = 'ChatGPT.exe' OR name = 'Codex.exe'")
            $running = Test-CodexDesktopRunning -Processes $processes
            # Also restart the bridge if it exits while the desktop is still open.
            if ($running -or $previous -ne $running) {
                $null = Set-X3BridgeState -DesktopRunning $running
            }
            if ($previous -ne $running) {
                "$(Get-Date -Format o) Codex desktop running: $running" | Add-Content "$PSScriptRoot\lifecycle.log"
            }
            $previous = $running
        } catch {
            "$(Get-Date -Format o) Watcher error: $($_.Exception.Message)" | Add-Content "$PSScriptRoot\lifecycle.log"
        }
        Start-Sleep -Seconds 5
    }
} finally {
    if ($ownsMutex) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
