$ErrorActionPreference = 'Stop'

function Test-CodexDesktopRunning {
    param([object[]]$Processes)
    foreach ($process in $Processes) {
        # The Store desktop app currently uses ChatGPT.exe; do not match the CLI.
        if ($process.Name -notin @('ChatGPT.exe', 'Codex.exe')) { continue }
        if ($process.ExecutablePath -match '(?i)\\WindowsApps\\OpenAI\.Codex_[^\\]+\\app\\(?:ChatGPT|Codex)\.exe$') {
            return $true
        }
    }
    return $false
}

function Set-X3BridgeState {
    param([bool]$DesktopRunning)
    if ($DesktopRunning) {
        & "$PSScriptRoot\Start-Bridge.ps1"
    } else {
        & "$PSScriptRoot\Stop-Bridge.ps1"
    }
}
