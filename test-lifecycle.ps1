$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Bridge-Lifecycle.ps1"
function Assert-Equal($Actual, $Expected, $Message) {
    if ($Actual -ne $Expected) { throw $Message }
}
$desktop = [pscustomobject]@{Name='ChatGPT.exe';ExecutablePath='C:\Program Files\WindowsApps\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0\app\ChatGPT.exe'}
$updated = [pscustomobject]@{Name='Codex.exe';ExecutablePath='C:\Program Files\WindowsApps\OpenAI.Codex_27.1.0_x64__2p2nqsd0c76g0\app\Codex.exe'}
$cli = [pscustomobject]@{Name='codex.exe';ExecutablePath='C:\Users\ExampleUser\AppData\Local\OpenAI\Codex\bin\version\codex.exe'}
$chat = [pscustomobject]@{Name='ChatGPT.exe';ExecutablePath='C:\Program Files\WindowsApps\OpenAI.ChatGPT_version\app\ChatGPT.exe'}
Assert-Equal (Test-CodexDesktopRunning @($desktop)) $true 'Desktop not detected'
Assert-Equal (Test-CodexDesktopRunning @($updated)) $true 'Updated package not detected'
Assert-Equal (Test-CodexDesktopRunning @($cli,$chat)) $false 'Unrelated process detected'
Assert-Equal (Test-CodexDesktopRunning @()) $false 'Empty list detected'
Assert-Equal (Test-CodexDesktopRunning @([pscustomobject]@{Name='ChatGPT.exe';ExecutablePath=$null})) $false 'Missing path detected'
Write-Output 'PASS: desktop, package version change, CLI/ChatGPT exclusion, no app, missing path'
