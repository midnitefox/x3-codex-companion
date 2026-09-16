# Firmware installation and recovery

This firmware replaces the reader application. It is for a compatible **Xteink X3 / ESP32-C3 / 16 MiB flash / 792 x 528 native panel**. It is not an X4 firmware. Firmware-locked variants are not supported. Do not guess pinouts or bypass a lock.

## Prepare

1. Complete `Setup.ps1`, then install build tools into the local environment:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
   ```

2. Stop all software holding the serial port. If this project's watcher is enabled, use `Disable-Autostart.ps1` first. Locate your port:

   ```powershell
   .\.venv\Scripts\python.exe -m serial.tools.list_ports -v
   ```

3. Connect the data cable. Enter the X3's supported download mode using the device's documented button procedure. On the tested unit, the owner held the device button while the connection entered flash mode. A power-only cable will not work. Use YOUR port in the commands below; COM3 is an example.

4. Check the chip and flash before writing:

   ```powershell
   .\.venv\Scripts\python.exe -m esptool --chip esp32c3 --port COM3 flash-id
   ```

## Back up before writing

Create a private local folder and read the full 16 MiB flash **only after verifying that size**:

```powershell
New-Item -ItemType Directory -Force backups
.\.venv\Scripts\python.exe -m esptool --chip esp32c3 --port COM3 read-flash 0 0x1000000 backups\x3-original.bin
Get-FileHash backups\x3-original.bin -Algorithm SHA256
```

A complete read must finish successfully and produce exactly 16,777,216 bytes. Keep the backup and hash outside Git. It can include private device settings. Do not share it in an issue.

Some native-USB X3 units fail large burst reads. For esptool **5.1.2**, the optional helper uses smaller stub transfers and checks the device's returned MD5 digest:

```powershell
.\.venv\Scripts\python.exe scripts/read_flash_conservative.py --chip esp32c3 --port COM3 read-flash 0 0x1000000 backups\x3-original.bin
```

The helper adapts an internal esptool method and is pinned to that version. Never treat a partial read as a backup. Obtain the device's actual partition table and active OTA application selection before writing. This repository does not auto-detect a safe application target for every device.

## Tested layout, not a universal assumption

The tested device had:

| Region | Offset | Size |
| --- | --- | --- |
| nvs | 0x9000 | 0x5000 |
| otadata | 0xe000 | 0x2000 |
| app0 | 0x10000 | 0x770000 |
| app1 | 0x780000 | 0x770000 |
| spiffs | 0xef0000 | 0x100000 |
| coredump | 0xff0000 | 0x10000 |

Its valid OTA selection pointed to app0. `firmware/partitions.csv` mirrors that layout. If your layout/active slot differs or cannot be confirmed, stop before writing and have someone familiar with ESP32 OTA partitions inspect your backup. Writing an app image into the wrong region can destroy data or leave the device unbootable.

## Build and flash the application only

```powershell
.\.venv\Scripts\pio.exe run -d firmware
```

The application is `firmware/.pio/build/x3status/firmware.bin`. Only when your verified active target is app0 at `0x10000`:

```powershell
.\.venv\Scripts\python.exe -m esptool --chip esp32c3 --port COM3 --baud 115200 --after hard-reset write-flash 0x10000 firmware/.pio/build/x3status/firmware.bin
```

Require esptool's successful hash verification. Do not use `erase-flash` or a bulk `pio run -t upload`; this procedure preserves bootloader, partition table, and settings. Release the button after the flash completes. The X3 should show its waiting screen. Start the bridge and look for a `frame_ack` in `bridge.log`, then check the physical display and a real input question. Enable the lifecycle watcher again if desired.

A prebuilt release binary, if offered, is application-only and has the same layout requirements. A binary alone does not establish compatibility.

## Recovery

Keep both your original full backup and the last working application binary. A previous compatible application can be written back to its verified application offset using the same application-only procedure. Full-flash restoration writes every region and overwrites settings; it is a recovery operation for the **same verified device and flash size**, not the routine update path. Get experienced help if the partition/OTA state is uncertain. The repository never uploads your backup or automatically flashes a connected device.

## After editing the interface

Live graphics are host-rendered and need no firmware update. To update built-in waiting/offline screens, run `generate_screens.py`, rebuild firmware, and repeat the backup/target checks before flashing. Without that step the old fallback graphics remain in firmware.
