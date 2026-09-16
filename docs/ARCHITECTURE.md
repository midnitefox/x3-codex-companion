# Architecture and limitations

```text
Codex desktop local IPC + local question events
                 -> Node status-source.cjs
                 -> Python bridge.py + display_ui.py
                 -> USB Serial/JTAG
                 -> ESP32-C3 firmware -> X3 e-ink panel
```

## Desktop adapter

Windows named pipe `\\.\pipe\codex-ipc`, with length-prefixed JSON frames. The adapter initializes a client, announces read-only following, and requests the desktop's followed-task set. It retains at most six tasks. It accepts version-11 snapshots and revision-matched patches. Unknown versions and revision gaps are rejected. Snapshots can contain conversation content in transit, but only title/status/request/error fields are retained; full snapshots are not written to disk. The bridge never submits a prompt or answers an approval.

Unanswered asynchronous questions are not reflected in the normal active flags in the tested app version. `question-state.cjs` therefore reads the exact local rollout path supplied by IPC, restricted to the user's Codex sessions directory (or CODEX_HOME/sessions). Initial reading scans that file; subsequent reads process appended bytes. The reader temporarily parses matching event records, stores only question IDs and pending counts, and removes answered IDs. It does not copy logs or retain question/answer text. Remote-host task logs are not covered by this fallback. If a local log cannot be read, normal IPC flags still work but async-question detection may be incomplete.

Task title previews are saved locally as `preview.png`. Logs contain statuses and USB outcomes, not full conversation histories. Both are ignored by Git.

## Display model

Status priority: Needs input, Failed, Working, Ready, Idle, Unknown. Counts are from fresh tracked tasks; missing or unknown tracked state makes totals unavailable. The monitor does not enumerate every historical task or ChatGPT conversation. Titles are uppercased, wrapped and truncated at a fixed bold font size.

## USB protocol

The host sends ASCII `X3HELLO` and requires `X3STATUS 1 792 528`. Frames have a 16-byte header: magic `X3ST`, little-endian uint32 sequence, payload length, and CRC32. Payload is exactly 52,272 monochrome bytes or zero bytes for a heartbeat. Pixels are MSB-first, 0 black / 1 white. Writes are paced in 256-byte chunks with a 3 ms gap to avoid overrunning native CDC receive buffers.

Firmware validates length and CRC before painting. ACK follows display refresh. A zero-length heartbeat after a reset/offline timeout is rejected with `ERROR NEED_FRAME`, causing a full-frame resend. Unchanged screens get heartbeats; changes are limited to one transfer every two seconds. Every twelfth painted frame uses a full refresh. There is no sleep, Wi-Fi, SD writing, or button handling in the docked prototype. Unplugged battery life is not optimized.

## Watcher

A per-user Startup shortcut launches a hidden PowerShell loop every sign-in. It checks for the Store Codex desktop executable by package path, currently ChatGPT.exe or Codex.exe, every five seconds. It deliberately excludes the CLI and the separate ChatGPT app. Non-Store distributions and future executable-path changes may need an update. A mutex prevents duplicate watchers. Keep the repository folder in place after enabling startup.
