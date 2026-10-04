<div align="center">
  <h1>🎵 SpotVault</h1>
  <p><strong>Spotify Playlist Archiving · Local Music Library · Android Sync</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-2F80ED.svg)](#-supported-platforms)
  [![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](#-requirements)

  [English](README.md) · [Türkçe](README.tr.md)

  <img src="docs/spotvault_gui.png" alt="SpotVault GUI" width="700">
</div>

## 📌 Overview

SpotVault is an open-source desktop utility for archiving Spotify playlists and albums into a local music library. It combines a graphical interface (GUI) and command-line workflows to handle track matching, local-file checks, M3U8 playlist generation, and direct Android USB transfer via ADB.

SpotVault uses external audio sources to retrieve tracks. **It does not require a Spotify account, does not download Spotify's original audio stream, and does not bypass DRM.** It works directly with public Spotify URLs.

## ⚡ Features

- **GUI & CLI Workflows**: Use the modern desktop interface (Bilingual: English & Turkish) or run tasks headless from the terminal.
- **Resilient Track Matching**: Matches Spotify metadata against external audio results using configurable duration tolerances and whitelists (`custom_labels.txt`).
- **Incremental Archiving**: Skips existing local files to save bandwidth and time.
- **Automated M3U8 Generation**: Creates compatible playlist files for modern music players.
- **Direct Android Sync**: Synchronizes your local library directly to a connected Android device over USB using ADB, complete with storage pre-checks.

## 🎵 Audio Formats & Transparency

SpotVault relies on underlying tools (like spotDL) to retrieve audio from supported public sources.

- **M4A / Source Format**: Preserving the source format avoids an additional lossy re-encoding step.
- **MP3 (320 kbps target)**: SpotVault can re-encode audio to MP3 for legacy compatibility. However, converting to a higher bitrate does not restore quality that was absent from the external source.

*Note: Automated matching may occasionally select an incorrect track version (e.g., a live version instead of studio). Reviewing your library after processing is recommended.*

## 🚀 Quick Start

### Windows
1. Download or clone the repository.
2. Run `start.bat`. (This will automatically set up the Python virtual environment and dependencies).
3. Paste a public Spotify playlist or album URL.
4. Click **Start Download**.

### Linux
```bash
git clone https://github.com/panehesy/spotvault.git
cd spotvault
chmod +x start.sh
./start.sh
```
*Depending on your distribution, you may need to install system packages manually if the script cannot resolve them (e.g., `sudo apt install python3 python3-tk ffmpeg adb`).*

### Manual Installation (Advanced)
If you prefer manual setup without the launchers:
```bash
python -m venv .venv
# Activate the virtual environment (.venv\Scripts\activate on Windows, source .venv/bin/activate on Linux)
pip install -r requirements.txt
python spotvault.py --help
```

## 📱 Android ADB Setup

To use the Android USB transfer feature:
1. Enable **Developer Options** on your Android device.
2. Enable **USB debugging**.
3. Connect the device to your computer.
4. Accept the **"Allow USB debugging"** prompt on the phone screen.

If the transfer fails or the device is shown as `unauthorized` in logs, unlock your phone, disconnect and reconnect the cable, and accept the authorization prompt.

## 🏗️ Architecture vs. Raw CLI Tools

While CLI tools like spotDL handle the raw downloading process, SpotVault acts as an **integrated archiving ecosystem** built around them:

- **State Management**: SpotVault remembers what's downloaded and manages a unified local pool or strict playlist folders.
- **Playlist Generation**: Automatically constructs UTF-8 M3U8 files with relative paths, ready for Android players.
- **Device Synchronization**: Eliminates the need for manual MTP drag-and-drop by wrapping ADB for fast, automated library pushes and MediaScanner triggers.
- **Visual Interface**: Provides a modern Dark Slate GUI for users who prefer visual feedback over terminal commands.

### Project Structure
```text
spotvault/
├── core/
│   ├── config.py             # Settings and persistence
│   ├── matcher.py            # Smart Official Matcher & Whitelists
│   ├── downloader.py         # Subprocess runner & diff-skip logic
│   ├── playlist_generator.py # M3U8 generation (standalone & pool)
│   ├── i18n.py               # TR/EN Translation Engine
│   └── adb_sync.py           # ADB discovery & file push engine
├── gui/
│   ├── app.py                # Tkinter desktop application
│   └── theme.py              # Cross-platform UI theme tokens
├── tests/                    # 57 Automated Unit & Integration Tests
├── docs/                     # Visual assets
├── spotvault.py              # Main CLI & GUI Entry point
└── start.bat / start.sh      # Automated environment setup launchers
```

## 🛠️ Troubleshooting

- **Application fails to start**: Run `python spotvault.py` directly from a terminal to view error outputs. Verify Python 3.10+ is installed.
- **Audio conversion fails**: Ensure `ffmpeg` is installed and available in your system's PATH.
- **Missing tracks**: Check `custom_labels.txt` or metadata differences.

## 📜 License & Disclaimers

SpotVault is an independent open-source project and is not affiliated with, endorsed by, or officially connected to Spotify, Google, or YouTube. It does not bypass DRM or decrypt protected audio. Users are responsible for complying with applicable copyright laws.

Distributed under the [MIT License](LICENSE).
