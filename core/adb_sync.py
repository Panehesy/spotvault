import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from core.config import resolve_adb_path


def parse_adb_devices_output(output: str) -> List[Dict[str, str]]:
    """
    Parses the standard stdout from 'adb devices' into a list of attached device records.
    """
    devices = []
    lines = output.strip().splitlines()
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("List of devices"):
            continue

        parts = line_clean.split()
        if len(parts) >= 2:
            devices.append({
                "serial": parts[0],
                "state": parts[1]
            })

    return devices


def parse_df_available_bytes(df_output: str) -> Optional[int]:
    """
    Parses 'df -k /sdcard' output on Android to extract free storage space in bytes.
    """
    lines = df_output.strip().splitlines()
    for line in lines:
        parts = line.split()
        if len(parts) >= 4 and parts[0].startswith("/") and parts[1].isdigit() and parts[3].isdigit():
            available_1k_blocks = int(parts[3])
            return available_1k_blocks * 1024

    for line in lines:
        parts = line.split()
        if len(parts) >= 6 and parts[3].isdigit():
            return int(parts[3]) * 1024

    return None


class AdbSyncEngine:
    """
    Android ADB synchronization engine managing connection status,
    storage capacity verification, file transfer, and MediaScanner indexing.
    """

    def __init__(
        self,
        adb_path: Optional[str] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> None:
        """
        Initializes the ADB engine with the resolved adb binary and event callbacks.
        """
        self.adb_bin = adb_path or resolve_adb_path() or "adb"
        self.log_callback = log_callback or (lambda msg: None)
        self.progress_callback = progress_callback or (lambda cur, tot, status: None)

    def log(self, message: str) -> None:
        """
        Transmits status messages to the UI or console logger.
        """
        self.log_callback(message)

    def run_adb_command(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Executes an ADB command and captures stdout and stderr.
        """
        full_cmd = [self.adb_bin] + args
        return subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )

    def get_device_status(self) -> Dict[str, Any]:
        """
        Queries attached Android devices and returns current connection state.
        """
        try:
            res = self.run_adb_command(["devices"])
            if res.returncode != 0:
                return {"connected": False, "serial": None, "state": "none", "error": res.stderr}

            devices = parse_adb_devices_output(res.stdout)
            if not devices:
                return {"connected": False, "serial": None, "state": "none"}

            for dev in devices:
                if dev["state"] == "device":
                    return {"connected": True, "serial": dev["serial"], "state": "device"}

            return {"connected": True, "serial": devices[0]["serial"], "state": devices[0]["state"]}
        except Exception as e:
            return {"connected": False, "serial": None, "state": "none", "error": str(e)}

    def get_available_storage_bytes(self, target_path: str = "/sdcard") -> Optional[int]:
        """
        Determines remaining free storage bytes on the connected Android device.
        """
        try:
            res = self.run_adb_command(["shell", "df", "-k", target_path])
            if res.returncode == 0:
                return parse_df_available_bytes(res.stdout)
        except Exception:
            pass
        return None

    def calculate_local_directory_size(self, local_path: Path) -> int:
        """
        Calculates the aggregate size in bytes of all files in the given local directory.
        """
        total = 0
        if not local_path.exists():
            return 0
        for root, _, files in os.walk(local_path):
            for f in files:
                fp = Path(root) / f
                try:
                    total += fp.stat().st_size
                except Exception:
                    pass
        return total

    def trigger_media_scanner(self, remote_path: str = "/sdcard/Music/Muzikler") -> None:
        """
        Broadcasts media scan intent to force Android to index freshly transferred audio files.
        """
        self.log(f"[ADB] Triggering Android MediaScanner for: {remote_path}")
        try:
            self.run_adb_command([
                "shell", "am", "broadcast",
                "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", f"file://{remote_path}"
            ])
        except Exception as e:
            self.log(f"[ADB] MediaScanner broadcast warning: {e}")

    def sync_library(
        self,
        local_music_dir: Union[str, Path],
        remote_music_dir: str = "/sdcard/Music/Muzikler",
        remote_playlist_dir: str = "/sdcard/Playlists"
    ) -> Dict[str, Any]:
        """
        Executes pre-checks, non-destructive file push, playlist transfer, and media scanning.
        """
        local_dir = Path(local_music_dir)
        if not local_dir.exists():
            raise FileNotFoundError(f"Local music directory not found: {local_dir}")

        status = self.get_device_status()
        if not status["connected"] or status["state"] != "device":
            raise ConnectionError(
                f"Device not ready. State: '{status.get('state')}'. Ensure USB Debugging is authorized."
            )

        local_bytes = self.calculate_local_directory_size(local_dir)
        free_bytes = self.get_available_storage_bytes(remote_music_dir)

        if free_bytes is not None and free_bytes < local_bytes:
            req_gb = local_bytes / (1024 ** 3)
            avail_gb = free_bytes / (1024 ** 3)
            raise IOError(
                f"Insufficient phone storage: {avail_gb:.2f} GB available, {req_gb:.2f} GB required."
            )

        self.log(f"[ADB] Creating remote directories on device: {remote_music_dir}")
        mk1 = self.run_adb_command(["shell", "mkdir", "-p", remote_music_dir])
        mk2 = self.run_adb_command(["shell", "mkdir", "-p", remote_playlist_dir])
        if mk1.returncode != 0:
            raise RuntimeError(f"Failed to create remote directory '{remote_music_dir}': {mk1.stderr.strip()}")

        self.log(f"[ADB] Starting incremental push from {local_dir} to {remote_music_dir}...")
        push_cmd = [self.adb_bin, "push", "--sync", str(local_dir) + "/.", remote_music_dir]

        process = subprocess.Popen(
            push_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                line_clean = line.strip()
                if line_clean:
                    self.log(f"[ADB] {line_clean}")

        process.wait()

        if process.returncode != 0:
            raise RuntimeError(f"ADB push failed with returncode {process.returncode}")

        # Synchronize M3U8 playlists directly to /sdcard/Playlists
        playlists_pushed = True
        playlists_source = local_dir / "Playlists"
        if playlists_source.exists() and any(playlists_source.glob("*.m3u8")):
            self.log(f"[ADB] Syncing playlists to {remote_playlist_dir}...")
            res = self.run_adb_command(["push", "--sync", str(playlists_source) + "/.", remote_playlist_dir])
            if res.returncode != 0:
                self.log(f"[ADB WARNING] Playlist push returned non-zero ({res.returncode}): {res.stderr.strip()}")
                playlists_pushed = False
            else:
                self.trigger_media_scanner(remote_playlist_dir)
        else:
            m3u8_files = [p for p in local_dir.rglob("*.m3u8") if p.is_file()]
            if m3u8_files:
                self.log(f"[ADB] Syncing {len(m3u8_files)} standalone playlist file(s) to {remote_playlist_dir}...")
                failed_pl = 0
                for pl in m3u8_files:
                    res = self.run_adb_command(["push", "--sync", str(pl), f"{remote_playlist_dir}/{pl.name}"])
                    if res.returncode != 0:
                        failed_pl += 1
                if failed_pl > 0:
                    self.log(f"[ADB WARNING] {failed_pl} playlist(s) encountered transfer errors.")
                    playlists_pushed = False
                else:
                    self.trigger_media_scanner(remote_playlist_dir)

        self.trigger_media_scanner(remote_music_dir)
        if playlists_pushed:
            self.log("[ADB] Sync completed successfully.")
        else:
            self.log("[ADB WARNING] Audio sync completed, but some playlist files failed to transfer.")

        return {
            "success": True,
            "playlists_synced": playlists_pushed,
            "transferred_bytes": local_bytes,
            "device": status["serial"]
        }
