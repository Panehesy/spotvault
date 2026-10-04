import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class SpotVaultConfig:
    """
    Data model and configuration manager for SpotVault Desktop.
    """
    audio_format: str = "mp3"
    bitrate: str = "320k"
    storage_mode: str = "standalone"
    embed_artwork: bool = True
    embed_metadata: bool = True
    download_lyrics: bool = False
    output_dir: str = "Downloads"
    adb_target: str = "/sdcard/Music/Muzikler"
    playlists_file: str = "playlists.txt"
    custom_labels: List[str] = field(default_factory=list)
    custom_labels_file: str = "custom_labels.txt"
    language: str = "tr"

    VALID_AUDIO_FORMATS = {"mp3", "m4a"}
    VALID_BITRATES = {"320k", "192k", "auto"}
    VALID_STORAGE_MODES = {"standalone", "pool_m3u8"}
    VALID_LANGUAGES = {"tr", "en"}

    def __post_init__(self) -> None:
        """
        Validates configuration field constraints upon initialization.
        """
        if self.language not in self.VALID_LANGUAGES:
            self.language = "tr"

        if self.audio_format not in self.VALID_AUDIO_FORMATS:
            raise ValueError(
                f"Invalid audio format '{self.audio_format}'. Supported: {sorted(self.VALID_AUDIO_FORMATS)}"
            )

        if self.bitrate not in self.VALID_BITRATES:
            raise ValueError(
                f"Invalid bitrate '{self.bitrate}'. Supported: {sorted(self.VALID_BITRATES)}"
            )

        if self.storage_mode not in self.VALID_STORAGE_MODES:
            raise ValueError(
                f"Invalid storage mode '{self.storage_mode}'. Supported: {sorted(self.VALID_STORAGE_MODES)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the configuration dataclass into a serializable dictionary.
        """
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """
        Serializes the configuration into a formatted JSON string.
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Union[str, Path]) -> None:
        """
        Persists the current configuration state to a JSON file on disk.
        """
        target_path = Path(path)
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
        except (IOError, OSError, ValueError) as e:
            raise IOError(f"Failed to persist SpotVault configuration to '{target_path}': {e}") from e

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpotVaultConfig":
        """
        Instantiates SpotVaultConfig from a dictionary, using defaults for missing fields.
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    @classmethod
    def from_json(cls, json_str: str) -> "SpotVaultConfig":
        """
        Parses a JSON string and constructs a validated SpotVaultConfig instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "SpotVaultConfig":
        """
        Loads configuration from a JSON file, or returns default configuration if missing.
        """
        target_path = Path(path)
        if not target_path.exists():
            return cls()

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls()


def resolve_adb_path() -> Optional[str]:
    """
    Resolves the adb executable path across Windows and Linux:
    1. On Windows: Bundled portable binary in core/adb/adb.exe, system PATH, legacy C:\\platform-tools\\adb.exe
    2. On Linux/macOS: System PATH, bundled core/adb/adb, standard system paths (/usr/bin/adb, /usr/local/bin/adb)
    """
    is_windows = sys.platform.startswith("win")
    binary_name = "adb.exe" if is_windows else "adb"

    bundled_adb = Path(__file__).resolve().parent / "adb" / binary_name
    if bundled_adb.exists() and (is_windows or os.access(str(bundled_adb), os.X_OK)):
        return str(bundled_adb)

    system_adb = shutil.which("adb")
    if system_adb:
        return system_adb

    if is_windows:
        legacy_adb = Path("C:/platform-tools/adb.exe")
        if legacy_adb.exists():
            return str(legacy_adb)
    else:
        for fallback in ["/usr/bin/adb", "/usr/local/bin/adb", "/opt/android-sdk/platform-tools/adb"]:
            if Path(fallback).exists():
                return fallback

    return None


def resolve_spotdl_path() -> Optional[str]:
    """
    Resolves the spotdl executable path across Windows and Linux:
    1. Bundled portable binary in core/spotdl.exe or core/spotdl
    2. System PATH
    """
    is_windows = sys.platform.startswith("win")
    binary_name = "spotdl.exe" if is_windows else "spotdl"

    system_spotdl = shutil.which("spotdl")
    if system_spotdl:
        return system_spotdl

    bundled_spotdl = Path(__file__).resolve().parent / binary_name
    if bundled_spotdl.exists() and (is_windows or os.access(str(bundled_spotdl), os.X_OK)):
        return str(bundled_spotdl)

    return None


def resolve_ffmpeg_path() -> Optional[str]:
    """
    Resolves the ffmpeg executable path across Windows and Linux:
    1. Bundled in core/ffmpeg.exe or core/ffmpeg
    2. System PATH
    3. User profile spotdl cache: ~/.spotdl/ffmpeg.exe (Windows) or ~/.spotdl/ffmpeg (Linux)
    4. Linux standard paths (/usr/bin/ffmpeg, /usr/local/bin/ffmpeg)
    """
    is_windows = sys.platform.startswith("win")
    binary_name = "ffmpeg.exe" if is_windows else "ffmpeg"

    bundled = Path(__file__).resolve().parent / binary_name
    if bundled.exists() and (is_windows or os.access(str(bundled), os.X_OK)):
        return str(bundled)

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    spotdl_ffmpeg = Path.home() / ".spotdl" / binary_name
    if spotdl_ffmpeg.exists() and (is_windows or os.access(str(spotdl_ffmpeg), os.X_OK)):
        return str(spotdl_ffmpeg)

    if not is_windows:
        for fallback in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
            if Path(fallback).exists():
                return fallback

    return None
