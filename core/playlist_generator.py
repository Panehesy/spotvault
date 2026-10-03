import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import mutagen


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".flac", ".ogg", ".wav"}


def inspect_audio_file(file_path: Path) -> Dict[str, Any]:
    """
    Extracts artist, title, and duration metadata from an audio file using mutagen,
    falling back to filename heuristics if tags are missing.
    """
    duration = -1
    artist = ""
    title = ""

    try:
        audio = mutagen.File(file_path)
        if audio and audio.info and hasattr(audio.info, "length"):
            duration = int(audio.info.length)

        if audio and hasattr(audio, "tags") and audio.tags:
            tags = audio.tags
            if hasattr(tags, "get"):
                raw_artist = tags.get("TPE1") or tags.get("\xa9ART") or tags.get("artist")
                raw_title = tags.get("TIT2") or tags.get("\xa9nam") or tags.get("title")

                if raw_artist:
                    artist = str(raw_artist[0] if isinstance(raw_artist, list) else raw_artist)
                if raw_title:
                    title = str(raw_title[0] if isinstance(raw_title, list) else raw_title)
    except Exception:
        pass

    if not artist or not title:
        stem = file_path.stem
        if " - " in stem:
            parts = stem.split(" - ", 1)
            artist = artist or parts[0].strip()
            title = title or parts[1].strip()
        else:
            title = title or stem
            artist = artist or "Unknown Artist"

    return {
        "artist": artist,
        "title": title,
        "duration": duration,
        "filename": file_path.name,
        "path": file_path
    }


def generate_m3u8_content(tracks: List[Dict[str, Any]]) -> str:
    """
    Constructs standard UTF-8 #EXTM3U playlist content with extended info tags and paths.
    """
    lines = ["#EXTM3U"]
    for track in tracks:
        duration = track.get("duration", -1)
        artist = track.get("artist", "Unknown Artist")
        title = track.get("title", "Unknown Title")
        rel_path = track.get("relative_path") or track.get("filename", "")

        lines.append(f"#EXTINF:{duration},{artist} - {title}")
        lines.append(rel_path.replace("\\", "/"))

    return "\n".join(lines) + "\n"


def write_playlist_file(playlist_path: Union[str, Path], tracks: List[Dict[str, Any]]) -> Path:
    """
    Writes track entries to a .m3u8 file encoded in UTF-8.
    """
    target = Path(playlist_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = generate_m3u8_content(tracks)
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    return target


def generate_all_playlists(
    output_dir: Union[str, Path],
    storage_mode: str = "standalone",
    pool_playlist_mapping: Optional[Dict[str, List[str]]] = None
) -> List[Path]:
    """
    Discovers local music files and generates M3U8 playlists for all albums/playlists
    in accordance with the configured storage architecture.
    """
    base_dir = Path(output_dir)
    generated_files: List[Path] = []

    if storage_mode == "standalone":
        for entry in base_dir.iterdir():
            if entry.is_dir() and entry.name not in {"Playlists", "Pool"}:
                audio_files = [
                    f for f in entry.iterdir()
                    if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
                ]
                if not audio_files:
                    continue

                audio_files.sort(key=lambda p: p.name.lower())
                tracks = []
                for af in audio_files:
                    meta = inspect_audio_file(af)
                    meta["relative_path"] = af.name
                    tracks.append(meta)

                playlist_file = entry / f"{entry.name}.m3u8"
                write_playlist_file(playlist_file, tracks)
                generated_files.append(playlist_file)

    elif storage_mode == "pool_m3u8":
        playlists_dir = base_dir / "Playlists"
        playlists_dir.mkdir(parents=True, exist_ok=True)
        pool_dir = base_dir / "Pool"
        mapping_file = playlists_dir / "pool_mapping.json"

        active_mapping: Dict[str, List[str]] = {}
        if mapping_file.exists():
            try:
                with open(mapping_file, "r", encoding="utf-8") as f:
                    active_mapping = json.load(f)
            except Exception:
                active_mapping = {}

        if pool_playlist_mapping:
            for pl_name, fnames in pool_playlist_mapping.items():
                existing_fnames = active_mapping.get(pl_name, [])
                for fn in fnames:
                    if fn not in existing_fnames:
                        existing_fnames.append(fn)
                active_mapping[pl_name] = existing_fnames

            try:
                with open(mapping_file, "w", encoding="utf-8") as f:
                    json.dump(active_mapping, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        if active_mapping:
            for pl_name, filenames in active_mapping.items():
                tracks = []
                for fname in filenames:
                    file_path = pool_dir / fname
                    meta = inspect_audio_file(file_path) if file_path.exists() else {"artist": "", "title": fname, "duration": -1}
                    meta["relative_path"] = f"../Pool/{fname}"
                    tracks.append(meta)

                playlist_file = playlists_dir / f"{pl_name}.m3u8"
                write_playlist_file(playlist_file, tracks)
                generated_files.append(playlist_file)
        elif pool_dir.exists():
            pool_files = [
                f for f in pool_dir.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
            ]
            if pool_files:
                pool_files.sort(key=lambda p: p.name.lower())
                tracks = []
                for pf in pool_files:
                    meta = inspect_audio_file(pf)
                    meta["relative_path"] = f"../Pool/{pf.name}"
                    tracks.append(meta)
                all_tracks_file = playlists_dir / "All_Tracks.m3u8"
                write_playlist_file(all_tracks_file, tracks)
                generated_files.append(all_tracks_file)

    return generated_files
