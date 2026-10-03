import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
import yt_dlp
import mutagen
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TRCK
from mutagen.mp4 import MP4, MP4Cover
from core.config import resolve_ffmpeg_path


RECORD_LABEL_WHITELIST = [
    # TR (Türkiye) Yerel Resmi Plak Şirketleri ve Distribütör Kanalları
    "netd müzik",
    "netd muzik",
    "avrupa müzik",
    "avrupa muzik",
    "poll production",
    "dmc",
    "seyhan müzik",
    "seyhan muzik",
    "dokuzsekiz müzik",
    "dokuzsekiz muzik",
    "kalan müzik",
    "kalan muzik",
    "epidemik",
    "pmc",
    "hiphoplife",
    "pasaj müzik",
    "pasaj muzik",
    "oss müzik",
    "oss muzik",
    "esen müzik",
    "esen muzik",
    "bkm",
    "sony music türkiye",
    "sony music turkey",
    "universal music turkey",
    "universal music türkiye",
    "warner music turkey",
    # Global Majör Yayıncılar
    "sony music",
    "universal music",
    "warner music",
    "vevo",
    "columbia records",
    "atlantic records",
    "interscope records",
    "republic records",
    "rca records",
    "def jam",
    "capitol records",
    "geffen records",
    "island records",
    "virgin music",
    # Global Bağımsız (Indie), Elektronik, Rock ve Metal Yayıncıları
    "spinnin'",
    "armada music",
    "ultra records",
    "ultra music",
    "defected",
    "monstercat",
    "anjunabeats",
    "hospital records",
    "sub pop",
    "xl recordings",
    "epitaph",
    "nuclear blast",
    "century media",
    "napalm records",
    "warp records",
    "beggars",
    "4ad",
    "rough trade",
    "domino recording",
    "matador records",
    "ninja tune",
    "mute records",
    "stones throw"
]


def load_custom_labels(file_path: Optional[Union[str, Path]] = None) -> List[str]:
    """
    Loads custom record labels from a text file, filtering empty lines and comments.
    """
    if file_path is None:
        file_path = Path(__file__).resolve().parent.parent / "custom_labels.txt"
    else:
        file_path = Path(file_path)

    if not file_path.exists():
        return []

    labels: List[str] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    labels.append(line_str.lower())
    except Exception:
        return []

    return list(dict.fromkeys(labels))


def get_active_whitelist(custom_labels: Optional[List[str]] = None) -> List[str]:
    """
    Returns the comprehensive active label whitelist by combining built-in labels,
    runtime custom labels, and entries from custom_labels.txt.
    """
    active = list(RECORD_LABEL_WHITELIST)
    if custom_labels:
        active.extend(lbl.lower().strip() for lbl in custom_labels if lbl and lbl.strip())

    file_labels = load_custom_labels()
    if file_labels:
        active.extend(file_labels)

    return list(dict.fromkeys(active))

BLACKLIST_KEYWORDS = [
    "slowed",
    "reverb",
    "speed up",
    "sped up",
    "cover",
    "canlı",
    "live",
    "bass boosted",
    "nightcore",
    "8d audio",
    "tiktok",
    "reaction",
    "karaoke",
    "instrumental",
    "teaser",
    "fragman",
    "behind the scenes",
    "kamera arkası"
]


def is_duration_acceptable(spotify_duration: float, yt_duration: float, tolerance: float = 3.0) -> bool:
    """
    Validates whether the YouTube video duration is within the acceptable tolerance of the Spotify track duration.
    """
    if spotify_duration <= 0 or yt_duration <= 0:
        return False
    return abs(spotify_duration - yt_duration) <= tolerance


def is_blacklisted(title: str, channel: str, original_title: Optional[str] = None) -> bool:
    """
    Checks if a candidate title or channel contains unwanted noise, fan edits, or unauthorized remixes.
    """
    normalized_title = title.lower()
    normalized_channel = channel.lower()
    combined = f"{normalized_title} {normalized_channel}"

    for kw in BLACKLIST_KEYWORDS:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, combined):
            return True

    if "remix" in normalized_title:
        original_has_remix = original_title is not None and "remix" in original_title.lower()
        if not original_has_remix:
            return True

    return False


def is_channel_whitelisted(channel: str, custom_labels: Optional[List[str]] = None) -> bool:
    """
    Determines if the given YouTube channel is a verified record label or an official Topic channel.
    Supports runtime custom labels and auto-loaded custom_labels.txt.
    """
    normalized = channel.lower().strip()

    if normalized.endswith("- topic") or normalized.endswith(" topic"):
        return True

    whitelist = get_active_whitelist(custom_labels=custom_labels)
    for label in whitelist:
        if label in normalized:
            return True

    return False


def score_candidate(
    spotify_info: Dict[str, Any],
    candidate: Dict[str, Any],
    tolerance: float = 3.0,
    custom_labels: Optional[List[str]] = None
) -> float:
    """
    Scores a candidate video based on channel authority, duration precision, and keyword cleanliness.
    Returns 0.0 if the candidate is disqualified.
    """
    title = candidate.get("title", "")
    channel = candidate.get("channel", "") or candidate.get("uploader", "")
    yt_duration = float(candidate.get("duration", 0) or 0)
    spotify_duration = float(spotify_info.get("duration", 0) or 0)
    original_title = spotify_info.get("title", "")

    if is_blacklisted(title, channel, original_title=original_title):
        return 0.0

    if not is_duration_acceptable(spotify_duration, yt_duration, tolerance=tolerance):
        return 0.0

    score = 100.0 - (abs(spotify_duration - yt_duration) * 10.0)

    if is_channel_whitelisted(channel, custom_labels=custom_labels):
        score += 50.0

    normalized_title = title.lower()
    if "official audio" in normalized_title or "official music video" in normalized_title or "official video" in normalized_title:
        score += 25.0

    artist = spotify_info.get("artist", "").lower()
    if artist and artist in channel.lower():
        score += 30.0

    return max(score, 1.0)


def search_youtube_candidates(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Searches YouTube for video candidates matching the query using yt-dlp without downloading media.
    """
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": f"ytsearch{max_results}"
    }

    candidates = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if result and "entries" in result:
                for entry in result["entries"]:
                    if entry:
                        candidates.append({
                            "id": entry.get("id"),
                            "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                            "title": entry.get("title", ""),
                            "channel": entry.get("channel") or entry.get("uploader", ""),
                            "duration": entry.get("duration", 0)
                        })
        except Exception:
            return []

    return candidates


def find_best_official_candidate(
    spotify_info: Dict[str, Any],
    max_candidates: int = 5,
    tolerance: float = 3.0,
    custom_labels: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Executes targeted queries to find the most accurate verified or official YouTube candidate.
    """
    title = spotify_info.get("title", "")
    artist = spotify_info.get("artist", "")
    queries = [
        f"{artist} - {title} official audio",
        f"{artist} - {title} official video",
        f"{artist} - {title}"
    ]

    best_candidate = None
    highest_score = 0.0

    for query in queries:
        candidates = search_youtube_candidates(query, max_results=max_candidates)
        for cand in candidates:
            score = score_candidate(
                spotify_info,
                cand,
                tolerance=tolerance,
                custom_labels=custom_labels
            )
            if score > highest_score:
                highest_score = score
                best_candidate = cand

        if highest_score >= 120.0:
            break

    return best_candidate


def fetch_spotify_track_metadata(spotify_url: str) -> Optional[Dict[str, Any]]:
    """
    Extracts track title, artist, duration, and cover URL from Spotify's public embed endpoints.
    Requires zero authentication or developer API tokens.
    """
    try:
        track_id_match = re.search(r"/track/([a-zA-Z0-9]+)", spotify_url)
        if not track_id_match:
            return None

        track_id = track_id_match.group(1)
        embed_url = f"https://open.spotify.com/embed/track/{track_id}"
        resp = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code != 200:
            return None

        html = resp.text
        scripts = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
        for s in scripts:
            try:
                data = json.loads(s)
                props = data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
                if props and "name" in props:
                    name = props.get("name")
                    artists = [a.get("name") for a in props.get("artists", [])]
                    artist_str = ", ".join([a for a in artists if a]) or "Unknown Artist"
                    duration_sec = int((props.get("duration", 0) or 0) / 1000)

                    cover_url = None
                    try:
                        oembed_resp = requests.get(f"https://open.spotify.com/oembed?url={spotify_url}", timeout=5)
                        if oembed_resp.status_code == 200:
                            cover_url = oembed_resp.json().get("thumbnail_url")
                    except Exception:
                        pass

                    return {
                        "title": name,
                        "artist": artist_str,
                        "duration": duration_sec,
                        "cover_url": cover_url
                    }
            except Exception:
                pass
    except Exception:
        pass

    return None


def embed_audio_metadata(
    file_path: Path,
    spotify_info: Dict[str, Any],
    cover_image_bytes: Optional[bytes] = None,
    audio_format: str = "mp3"
) -> None:
    """
    Embeds track metadata (title, artist, album, track number, cover artwork) into the downloaded audio file.
    """
    title = spotify_info.get("title", "")
    artist = spotify_info.get("artist", "")
    album = spotify_info.get("album", "")
    year = str(spotify_info.get("year", ""))
    track_num = spotify_info.get("track_number", 1)

    if audio_format == "mp3":
        try:
            tags = ID3(file_path)
        except Exception:
            tags = ID3()

        if title:
            tags["TIT2"] = TIT2(encoding=3, text=title)
        if artist:
            tags["TPE1"] = TPE1(encoding=3, text=artist)
        if album:
            tags["TALB"] = TALB(encoding=3, text=album)
        if year:
            tags["TDRC"] = TDRC(encoding=3, text=year)
        if track_num:
            tags["TRCK"] = TRCK(encoding=3, text=str(track_num))

        if cover_image_bytes:
            tags["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=cover_image_bytes
            )
        tags.save(file_path)

    elif audio_format == "m4a":
        try:
            mp4_file = MP4(file_path)
            if title:
                mp4_file["\xa9nam"] = [title]
            if artist:
                mp4_file["\xa9ART"] = [artist]
            if album:
                mp4_file["\xa9alb"] = [album]
            if year:
                mp4_file["\xa9day"] = [year]
            if track_num:
                mp4_file["trkn"] = [(int(track_num), 0)]

            if cover_image_bytes:
                mp4_file["covr"] = [
                    MP4Cover(cover_image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
                ]
            mp4_file.save()
        except Exception:
            pass


def download_and_tag_track(
    video_url: str,
    output_target: Path,
    spotify_info: Dict[str, Any],
    audio_format: str = "mp3",
    bitrate: str = "320k",
    embed_artwork: bool = True,
    embed_metadata: bool = True
) -> bool:
    """
    Downloads audio stream using yt-dlp, formats it to the specified codec and bitrate, and embeds Spotify tags.
    """
    output_target.parent.mkdir(parents=True, exist_ok=True)
    temp_template = str(output_target.with_suffix(".temp.%(ext)s"))

    ydl_opts = {
        "format": "ba/b",
        "outtmpl": temp_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": bitrate.replace("k", "") if bitrate != "auto" else "0"
        }]
    }

    ffmpeg_bin = resolve_ffmpeg_path()
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = str(Path(ffmpeg_bin).parent)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        final_temp_path = output_target.with_name(f"{output_target.stem}.temp.{audio_format}")
        if not final_temp_path.exists():
            return False

        if output_target.exists():
            output_target.unlink()
        final_temp_path.rename(output_target)

        cover_bytes = None
        cover_url = spotify_info.get("cover_url")
        if embed_artwork and cover_url:
            try:
                resp = requests.get(cover_url, timeout=10)
                if resp.status_code == 200:
                    cover_bytes = resp.content
            except Exception:
                cover_bytes = None

        if embed_metadata:
            embed_audio_metadata(
                output_target,
                spotify_info,
                cover_image_bytes=cover_bytes,
                audio_format=audio_format
            )

        return True
    except Exception:
        return False
