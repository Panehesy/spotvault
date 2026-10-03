import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from core.config import SpotVaultConfig, resolve_spotdl_path
from core.matcher import find_best_official_candidate, download_and_tag_track, fetch_spotify_track_metadata


INVALID_FILENAME_CHARS = r'[<>:"/\\|?*]'


def sanitize_filename(name: str) -> str:
    """
    Cleans a string to be safely used as a Windows filename or directory name.
    """
    sanitized = re.sub(INVALID_FILENAME_CHARS, "_", name)
    sanitized = sanitized.strip(". ")
    return sanitized if sanitized else "Untitled"


def is_track_already_downloaded(
    output_dir: Union[str, Path],
    playlist_name: str,
    artist: str,
    title: str,
    audio_format: str = "mp3",
    storage_mode: str = "standalone"
) -> bool:
    """
    Performs a 0.001-second local filesystem existence check to avoid redundant network queries.
    """
    clean_artist = sanitize_filename(artist)
    clean_title = sanitize_filename(title)
    filename = f"{clean_artist} - {clean_title}.{audio_format}"

    base_dir = Path(output_dir)
    if storage_mode == "pool_m3u8":
        target_path = base_dir / "Pool" / filename
    else:
        clean_playlist = sanitize_filename(playlist_name)
        target_path = base_dir / clean_playlist / filename

    return target_path.exists() and target_path.stat().st_size > 0


def build_spotdl_command(
    url: str,
    config: SpotVaultConfig,
    playlist_name: Optional[str] = None
) -> List[str]:
    """
    Constructs the exact CLI argument vector for spotDL execution with configured flags.
    """
    spotdl_bin = resolve_spotdl_path() or "spotdl"

    args = [spotdl_bin, "download", url]

    args.extend(["--format", config.audio_format])
    args.extend(["--bitrate", config.bitrate])

    if not config.embed_artwork:
        args.append("--skip-album-art")

    if not config.embed_metadata:
        args.append("--no-metadata")

    if config.download_lyrics:
        args.append("--generate-lrc")

    args.append("--only-verified-results")

    base_output = Path(config.output_dir).as_posix()
    if config.storage_mode == "pool_m3u8":
        output_tmpl = f"{base_output}/Pool/{{artist}} - {{title}}.{{output-ext}}"
    else:
        if playlist_name:
            folder = sanitize_filename(playlist_name)
        elif "/track/" in url:
            folder = "Singles"
        else:
            folder = "{playlist}"
        output_tmpl = f"{base_output}/{folder}/{{artist}} - {{title}}.{{output-ext}}"

    args.extend(["--output", output_tmpl])

    return args


class SpotVaultDownloader:
    """
    High-level orchestrator executing spotDL downloads with diff-skip checks
    and automatic Smart Official Matcher fallbacks for unverified tracks.
    """

    def __init__(
        self,
        config: SpotVaultConfig,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> None:
        """
        Initializes the downloader engine with configuration and output streaming callbacks.
        """
        self.config = config
        self.log_callback = log_callback or (lambda msg: None)
        self.progress_callback = progress_callback or (lambda cur, tot, status: None)

    def log(self, message: str) -> None:
        """
        Emits log entries to the configured receiver.
        """
        self.log_callback(message)

    def download_playlist(
        self,
        playlist_url: str,
        playlist_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes verified spotDL sync and triggers fallback matcher for missing tracks.
        """
        stats = {
            "total": 0,
            "downloaded": 0,
            "skipped": 0,
            "fallback_matched": 0,
            "failed": 0
        }

        cmd = build_spotdl_command(playlist_url, self.config, playlist_name=playlist_name)
        self.log(f"[SPOTDL] Starting download for: {playlist_url}")

        failed_tracks: List[Dict[str, Any]] = []
        current_query: Optional[str] = playlist_url if "/track/" in playlist_url else None

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                    self.log(line_clean)

                    if line_clean.startswith("Processing query:"):
                        current_query = line_clean.replace("Processing query:", "").strip()

                    if "Skipping" in line_clean or "already exists" in line_clean:
                        stats["skipped"] += 1
                    elif "Downloaded" in line_clean:
                        stats["downloaded"] += 1
                    elif (
                        "No verified result found" in line_clean
                        or "LookupError" in line_clean
                        or "AudioProviderError" in line_clean
                        or "returned no usable results" in line_clean
                        or "JSONDecodeError" in line_clean
                    ):
                        match = re.search(r'for "([^"]+)"', line_clean)
                        if match:
                            failed_tracks.append({"query": match.group(1)})
                        elif current_query and not any(f["query"] == current_query for f in failed_tracks):
                            failed_tracks.append({"query": current_query})

            process.wait()
            if process.returncode != 0 and not stats["downloaded"] and not stats["skipped"] and not failed_tracks:
                failed_tracks.append({"query": playlist_url})
        except Exception as e:
            self.log(f"[ERROR] spotDL execution error: {e}")
            if not stats["downloaded"] and not stats["skipped"]:
                failed_tracks.append({"query": playlist_url})

        if failed_tracks:
            self.log(f"[MATCHER] {len(failed_tracks)} tracks missed by spotDL. Activating Smart Official Matcher...")
            for item in failed_tracks:
                query = item.get("query", "")
                if not query:
                    continue

                spotify_info = None
                if "/track/" in query:
                    self.log(f"[MATCHER] Resolving Spotify metadata for: {query}")
                    spotify_info = fetch_spotify_track_metadata(query)

                if not spotify_info:
                    parts = query.split(" - ", 1)
                    artist = parts[0].strip() if len(parts) > 1 else ""
                    title = parts[1].strip() if len(parts) > 1 else query.strip()
                    spotify_info = {
                        "artist": artist,
                        "title": title,
                        "duration": 0
                    }

                cand = find_best_official_candidate(
                    spotify_info,
                    custom_labels=self.config.custom_labels
                )
                if cand:
                    self.log(f"[MATCHER] Found official match: '{cand['title']}' on '{cand['channel']}'")
                    clean_folder = sanitize_filename(playlist_name or ("Singles" if "/track/" in query else "Tracks"))
                    clean_artist = sanitize_filename(spotify_info.get("artist") or "Unknown Artist")
                    clean_title = sanitize_filename(spotify_info.get("title") or "Unknown Title")
                    target_file = Path(self.config.output_dir) / clean_folder / f"{clean_artist} - {clean_title}.{self.config.audio_format}"

                    success = download_and_tag_track(
                        video_url=cand["url"],
                        output_target=target_file,
                        spotify_info=spotify_info,
                        audio_format=self.config.audio_format,
                        bitrate=self.config.bitrate,
                        embed_artwork=self.config.embed_artwork,
                        embed_metadata=self.config.embed_metadata
                    )
                    if success:
                        stats["fallback_matched"] += 1
                        self.log(f"[MATCHER] Successfully downloaded and tagged: {target_file.name}")
                    else:
                        stats["failed"] += 1
                        self.log(f"[MATCHER] Failed to download or convert: {cand['title']}")
                else:
                    stats["failed"] += 1
                    self.log(f"[MATCHER] No compliant official release found for: {query}")

        stats["total"] = stats["downloaded"] + stats["skipped"] + stats["fallback_matched"] + stats["failed"]
        return stats
