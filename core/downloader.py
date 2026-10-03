import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from core.config import SpotVaultConfig, resolve_spotdl_path
from core.matcher import find_best_official_candidate, download_and_tag_track, fetch_spotify_track_metadata


INVALID_FILENAME_CHARS = r'[<>:"/\\|?*]'


def sanitize_filename(name: str, max_length: int = 120) -> str:
    """
    Cleans a string to be safely used as a Windows filename or directory name,
    enforcing max_length truncation to prevent Windows MAX_PATH (260 char) overflows.
    """
    sanitized = re.sub(INVALID_FILENAME_CHARS, "_", name)
    sanitized = sanitized.strip(". ")
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip(". ")
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
    Performs a local filesystem existence check to avoid redundant network queries.
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


def reconcile_pool_tracks(
    pool_dir: Path,
    queries: List[str],
    audio_format: str = "mp3"
) -> List[str]:
    """
    Given a list of track queries (e.g. 'Artist - Title') and a Pool directory,
    identifies all existing files in Pool that match those queries, ensuring cached
    and cross-playlist shared tracks are never dropped from generated playlists.
    """
    if not pool_dir.exists():
        return []

    pool_files = {f.name: f for f in pool_dir.glob("*.*") if f.is_file()}
    matched: List[str] = []

    for q in queries:
        parts = q.split(" - ", 1)
        artist = sanitize_filename(parts[0].strip() if len(parts) > 1 else "")
        title = sanitize_filename(parts[1].strip() if len(parts) > 1 else q.strip())

        # 1. Exact expected filename match
        exact_name = f"{artist} - {title}.{audio_format}"
        if exact_name in pool_files:
            matched.append(exact_name)
            continue

        # 2. Case-insensitive or extension-agnostic match
        target_stem = f"{artist} - {title}".lower()
        found = False
        for fname, fpath in pool_files.items():
            if fpath.stem.lower() == target_stem:
                matched.append(fname)
                found = True
                break
        if found:
            continue

        # 3. Substring matching if both artist and title are contained
        if artist and title:
            for fname in pool_files.keys():
                fl = fname.lower()
                if artist.lower() in fl and title.lower() in fl:
                    matched.append(fname)
                    break

    return list(dict.fromkeys(matched))


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
        self.cancel_requested: bool = False
        self.active_process: Optional[subprocess.Popen] = None
        self.pool_playlist_mapping: Dict[str, List[str]] = {}

    def log(self, message: str) -> None:
        """
        Emits log entries to the configured receiver.
        """
        self.log_callback(message)

    def cancel(self) -> None:
        """
        Signals cancellation to stop ongoing spotDL or matcher download tasks.
        """
        self.cancel_requested = True
        self.log("[INFO] Cancellation requested by user...")
        if self.active_process and self.active_process.poll() is None:
            try:
                self.active_process.terminate()
            except Exception:
                pass

    def download_playlist(
        self,
        playlist_url: str,
        playlist_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes verified spotDL sync and triggers fallback matcher for missing tracks.
        """
        self.cancel_requested = False
        stats = {
            "total": 0,
            "downloaded": 0,
            "skipped": 0,
            "fallback_matched": 0,
            "failed": 0
        }

        clean_folder = sanitize_filename(playlist_name or ("Singles" if "/track/" in playlist_url else "Tracks"))
        cmd = build_spotdl_command(playlist_url, self.config, playlist_name=playlist_name)
        self.log(f"[SPOTDL] Starting download for: {playlist_url}")

        failed_tracks: List[Dict[str, Any]] = []
        seen_queries: List[str] = []
        current_query: Optional[str] = playlist_url if "/track/" in playlist_url else None

        pool_dir = Path(self.config.output_dir) / "Pool"
        initial_pool_files = set(f.name for f in pool_dir.glob("*.*")) if pool_dir.exists() else set()

        try:
            self.active_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            if self.active_process.stdout:
                for line in iter(self.active_process.stdout.readline, ""):
                    if self.cancel_requested:
                        try:
                            self.active_process.terminate()
                        except Exception:
                            pass
                        self.log("[INFO] spotDL process stopped upon user request.")
                        break

                    line_clean = line.strip()
                    if not line_clean:
                        continue
                    self.log(line_clean)

                    if line_clean.startswith("Processing query:"):
                        current_query = line_clean.replace("Processing query:", "").strip()
                        if current_query and current_query not in seen_queries:
                            seen_queries.append(current_query)

                    if "Skipping" in line_clean or "already exists" in line_clean:
                        stats["skipped"] += 1
                        m_quote = re.search(r'["\']([^"\']+)["\']', line_clean)
                        if m_quote and m_quote.group(1) not in seen_queries:
                            seen_queries.append(m_quote.group(1))
                    elif "Downloaded" in line_clean:
                        stats["downloaded"] += 1
                        m_quote = re.search(r'["\']([^"\']+)["\']', line_clean)
                        if m_quote and m_quote.group(1) not in seen_queries:
                            seen_queries.append(m_quote.group(1))
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

            self.active_process.wait()
            if self.active_process.returncode != 0 and not stats["downloaded"] and not stats["skipped"] and not failed_tracks:
                if not self.cancel_requested:
                    failed_tracks.append({"query": playlist_url})
        except Exception as e:
            self.log(f"[ERROR] spotDL execution error: {e}")
            if not stats["downloaded"] and not stats["skipped"] and not self.cancel_requested:
                failed_tracks.append({"query": playlist_url})
        finally:
            self.active_process = None

        if self.config.storage_mode == "pool_m3u8" and pool_dir.exists():
            current_pool_files = set(f.name for f in pool_dir.glob("*.*"))
            new_or_existing = current_pool_files - initial_pool_files
            reconciled = reconcile_pool_tracks(
                pool_dir=pool_dir,
                queries=seen_queries,
                audio_format=self.config.audio_format
            )
            mapping_list = self.pool_playlist_mapping.setdefault(clean_folder, [])
            for fname in reconciled:
                if fname not in mapping_list:
                    mapping_list.append(fname)
            for fname in new_or_existing:
                if fname not in mapping_list:
                    mapping_list.append(fname)

        if failed_tracks and not self.cancel_requested:
            self.log(f"[MATCHER] {len(failed_tracks)} tracks missed by spotDL. Activating Smart Official Matcher...")
            for item in failed_tracks:
                if self.cancel_requested:
                    self.log("[INFO] Smart Matcher fallback cancelled by user.")
                    break

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

                clean_artist = sanitize_filename(spotify_info.get("artist") or "Unknown Artist")
                clean_title = sanitize_filename(spotify_info.get("title") or "Unknown Title")
                track_filename = f"{clean_artist} - {clean_title}.{self.config.audio_format}"

                if is_track_already_downloaded(
                    output_dir=self.config.output_dir,
                    playlist_name=clean_folder,
                    artist=clean_artist,
                    title=clean_title,
                    audio_format=self.config.audio_format,
                    storage_mode=self.config.storage_mode
                ):
                    self.log(f"[DIFF-SKIP] Track already archived locally: {track_filename}")
                    stats["skipped"] += 1
                    if self.config.storage_mode == "pool_m3u8":
                        if track_filename not in self.pool_playlist_mapping.setdefault(clean_folder, []):
                            self.pool_playlist_mapping[clean_folder].append(track_filename)
                    continue

                cand = find_best_official_candidate(
                    spotify_info,
                    custom_labels=self.config.custom_labels
                )
                if cand:
                    self.log(f"[MATCHER] Found official match: '{cand['title']}' on '{cand['channel']}'")
                    if self.config.storage_mode == "pool_m3u8":
                        target_file = Path(self.config.output_dir) / "Pool" / track_filename
                    else:
                        target_file = Path(self.config.output_dir) / clean_folder / track_filename

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
                        if self.config.storage_mode == "pool_m3u8":
                            if track_filename not in self.pool_playlist_mapping.setdefault(clean_folder, []):
                                self.pool_playlist_mapping[clean_folder].append(track_filename)
                    else:
                        stats["failed"] += 1
                        self.log(f"[MATCHER] Failed to download or convert: {cand['title']}")
                else:
                    stats["failed"] += 1
                    self.log(f"[MATCHER] No compliant official release found for: {query}")

        stats["total"] = stats["downloaded"] + stats["skipped"] + stats["fallback_matched"] + stats["failed"]
        return stats
