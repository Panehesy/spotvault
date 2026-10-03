import argparse
import sys
from pathlib import Path
from typing import List, Optional

from core.adb_sync import AdbSyncEngine
from core.config import SpotVaultConfig
from core.downloader import SpotVaultDownloader
from core.playlist_generator import generate_all_playlists


def parse_cli_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses command line arguments, defaulting to GUI mode if no CLI action parameters are supplied.
    """
    parser = argparse.ArgumentParser(
        description="SpotVault v1.0.1 — Offline Spotify Downloader & Android ADB Sync Studio"
    )

    parser.add_argument("--gui", action="store_true", help="Launch the graphical interface")
    parser.add_argument("--cli", action="store_true", help="Force headless command-line execution")
    parser.add_argument("--url", type=str, help="Single Spotify playlist, album, or track URL to download")
    parser.add_argument("--file", type=str, help="Path to text file containing Spotify URLs (default: playlists.txt)")
    parser.add_argument("--format", choices=["mp3", "m4a"], help="Audio codec format")
    parser.add_argument("--bitrate", choices=["320k", "192k", "auto"], help="Audio bitrate")
    parser.add_argument("--storage-mode", choices=["standalone", "pool_m3u8"], help="Storage organization mode")
    parser.add_argument("--output-dir", type=str, help="Custom local download directory")
    parser.add_argument("--sync-adb", action="store_true", help="Transfer downloaded library to Android via ADB")
    parser.add_argument("--generate-playlists", action="store_true", help="Regenerate M3U8 playlists without downloading")

    if args is None:
        args = sys.argv[1:]

    parsed = parser.parse_args(args)

    # Clean execution mode resolution
    if parsed.gui:
        parsed.gui = True
    elif parsed.cli or parsed.url or parsed.file or parsed.sync_adb or parsed.generate_playlists:
        parsed.gui = False
    else:
        # Default with no arguments is GUI
        parsed.gui = True

    return parsed


def run_cli_pipeline(args: argparse.Namespace, config: SpotVaultConfig) -> int:
    """
    Executes headless operations according to specified command-line parameters.
    Returns 0 on complete success, 1 on download/validation error, 2 on ADB failure.
    """
    def cli_log(msg: str) -> None:
        print(msg, flush=True)

    if args.format:
        config.audio_format = args.format
    if args.bitrate:
        config.bitrate = args.bitrate
    if args.storage_mode:
        config.storage_mode = args.storage_mode

    # Path resolution: user-specified path resolves relative to CWD; default resolves relative to script dir
    if args.output_dir:
        config.output_dir = args.output_dir
        base_dir = Path(args.output_dir)
        if not base_dir.is_absolute():
            base_dir = (Path.cwd() / base_dir).resolve()
    else:
        base_dir = Path(config.output_dir)
        if not base_dir.is_absolute():
            base_dir = (Path(__file__).resolve().parent / base_dir).resolve()

    if args.generate_playlists:
        cli_log("[SPOTVAULT] Regenerating M3U8 playlists...")
        try:
            created = generate_all_playlists(output_dir=base_dir, storage_mode=config.storage_mode)
            cli_log(f"[SPOTVAULT] {len(created)} playlist(s) generated successfully.")
            return 0
        except Exception as e:
            cli_log(f"[SPOTVAULT ERROR] Playlist generation failed: {e}")
            return 1

    urls: List[str] = []
    if args.url:
        u = args.url.strip()
        if u.startswith("http://") or u.startswith("https://") or u.startswith("spotify:"):
            urls.append(u)
        else:
            cli_log(f"[SPOTVAULT WARNING] Provided URL format is unexpected: {u}")
            urls.append(u)
    else:
        if args.file:
            url_file = Path(args.file)
            if not url_file.is_absolute():
                url_file = (Path.cwd() / url_file).resolve()
        else:
            url_file = Path.cwd() / config.playlists_file
            if not url_file.exists():
                script_dir_file = Path(__file__).resolve().parent / config.playlists_file
                if script_dir_file.exists():
                    url_file = script_dir_file

        if url_file.exists():
            for line in url_file.read_text(encoding="utf-8").splitlines():
                clean_line = line.split("#")[0].strip()
                if not clean_line:
                    continue
                if clean_line.startswith("http://") or clean_line.startswith("https://") or clean_line.startswith("spotify:"):
                    urls.append(clean_line)
                else:
                    cli_log(f"[SPOTVAULT WARNING] Skipping malformed line in playlist file: {clean_line}")
        elif args.file:
            cli_log(f"[SPOTVAULT ERROR] Specified playlist file not found: {url_file}")
            return 1

    total_failed = 0

    if urls:
        cli_log(f"[SPOTVAULT] Starting download queue for {len(urls)} target(s)...")
        downloader = SpotVaultDownloader(config, log_callback=cli_log)
        for i, u in enumerate(urls, 1):
            cli_log(f"\n[{i}/{len(urls)}] Processing: {u}")
            try:
                stats = downloader.download_playlist(u)
                failed_count = stats.get("failed", 0) if isinstance(stats, dict) else 0
                total_failed += failed_count
                if failed_count > 0:
                    cli_log(f"[SPOTVAULT WARNING] {failed_count} track(s) failed in this playlist.")
            except Exception as e:
                cli_log(f"[SPOTVAULT ERROR] Unhandled error processing {u}: {e}")
                total_failed += 1

        cli_log("\n[SPOTVAULT] Downloads finished. Generating playlists...")
        try:
            generate_all_playlists(output_dir=base_dir, storage_mode=config.storage_mode)
        except Exception as e:
            cli_log(f"[SPOTVAULT WARNING] M3U8 generation encounter: {e}")
    elif not args.sync_adb:
        cli_log("[SPOTVAULT] No URLs provided. Specify --url, --file, or populate playlists.txt.")
        return 1

    if args.sync_adb:
        cli_log("\n[SPOTVAULT] Starting Android ADB synchronization...")
        adb = AdbSyncEngine(log_callback=cli_log)
        try:
            res = adb.sync_library(local_music_dir=base_dir, remote_music_dir=config.adb_target)
            trans_mb = res.get("transferred_bytes", 0) / (1024 * 1024)
            cli_log(f"[SPOTVAULT] Sync completed successfully ({trans_mb:.2f} MB transferred).")
        except Exception as e:
            cli_log(f"[SPOTVAULT ERROR] ADB sync failed: {e}")
            return 2

    return 1 if total_failed > 0 else 0


def main() -> None:
    """
    Main application entrypoint branching to GUI or headless CLI mode.
    """
    config_path = Path(__file__).resolve().parent / "spotvault_config.json"
    config = SpotVaultConfig.load(config_path)

    args = parse_cli_arguments()

    if args.gui:
        from gui.app import launch_gui
        launch_gui()
    else:
        sys.exit(run_cli_pipeline(args, config))


if __name__ == "__main__":
    main()
