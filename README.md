# 🎵 SpotVault

> **Automated, Zero-Setup Spotify Playlist Archiving Pipeline**  
> *A hardened, portable batch automation layer built on top of the open-source [spotDL](https://github.com/spotDL/spotify-downloader) engine.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows)](start.bat)
[![Upstream: spotDL](https://img.shields.io/badge/Upstream-spotDL%20v4.5-green.svg)](https://github.com/spotDL/spotify-downloader)
[![Quality: 320k](https://img.shields.io/badge/Audio-320%20kbps%20MP3-brightgreen.svg)](#-key-features)
[![Dependencies](https://img.shields.io/badge/Python%20%26%20FFmpeg-Self--Contained-orange.svg)](#-overview)

---

## 📌 Overview

**SpotVault** is a streamlined, portable distribution designed for batch downloading and organizing Spotify playlists. Built on top of the Python-based **spotDL** engine and **FFmpeg**, it packages all necessary dependencies and batch automation into a single, double-clickable pipeline without requiring you to manually install Python or configure system-wide FFmpeg in your Windows PATH.

---

## 🚀 Key Features

* **⚡ Self-Contained & Portable:** While powered by Python and FFmpeg under the hood, SpotVault bundles the runtime into a standalone engine. You do not need to install Python on Windows or manually configure FFmpeg in your system PATH.
* **🛡️ Bot-Detection Bypass:** Includes pre-configured mobile client emulation to prevent stream access blocks (`HTTP 403`).
* **💎 Official Audio Guarantee (`--only-verified-results`):** Strictly enforces downloads from verified distributor audio (Official Artist Channels, Topic, VEVO). Rejects user-uploaded clips, lyric videos, and fan edits.
* **📁 Multi-Playlist Batch Queue:** Reads all URLs line-by-line from `playlists.txt` and automatically creates dedicated folders for each playlist.
* **🎨 Embedded Metadata & Artwork:** Pulls original 640x640 cover art, track numbering, artist, and album tags directly from Spotify and embeds them into 320 kbps MP3 files.
* **🔄 Smart Resume:** Safely interrupt anytime; already downloaded songs are automatically skipped upon restart.

---

## 📊 Comparison

| Feature | Direct Stream Tools | Web-Bridge Tools | Standard CLI | **SpotVault** |
| :--- | :---: | :---: | :---: | :---: |
| **Free Account Compatibility** | ❌ Severely Restricted | ✅ Yes | ✅ Yes | **✅ Yes (Zero Login Needed)** |
| **Bot-Block Bypass** | N/A | N/A | ❌ Can hit 403 | **✅ Pre-configured (Emulated)** |
| **Official Audio Enforcement** | N/A | ✅ Yes | ⚠️ Manual flag | **✅ Enforced by Default** |
| **Batch Playlist Queue** | ❌ Rate-limited | ❌ Server cooldowns | ⚠️ Manual scripting | **✅ Automated (`playlists.txt`)** |
| **Auto Per-Playlist Folders** | Manual | Manual | ⚠️ Manual flag | **✅ Automatic (`Downloads/{list}`)** |
| **System Installation** | Python / Runtimes | Browser / Web | Manual Python + FFmpeg | **✅ Portable (No Manual Install)** |

---

## 🛠️ Quick Start

### 1. Download
Clone this repository or download the ZIP:
```bash
git clone https://github.com/Panehesy/spotvault.git
cd spotvault
```

### 2. Add Your Playlists
1. Copy `playlists.example.txt` to `playlists.txt` (or launch `start.bat` once to auto-generate it).
2. Paste your Spotify playlist URLs into `playlists.txt` (one per line):
   ```text
   https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd
   ```

### 3. Run
Double-click **`start.bat`**.

All files will be downloaded and structured automatically:
```text
Downloads/
├── Playlist Name 1/
│   ├── Artist - Song Title 1.mp3
│   └── Artist - Song Title 2.mp3
└── Playlist Name 2/
    ├── Artist - Song Title 3.mp3
    └── ...
```

---

## 📦 Project Structure

```text
spotvault/
├── start.bat                  # One-click Windows launcher
├── playlists.example.txt      # Playlist URL template
├── playlists.txt              # Active download queue (git-ignored)
├── LICENSE                    # MIT License
├── README.md                  # Documentation
└── core/                      # Portable engine & runner
    ├── spotdl.exe             # Standalone downloader engine
    └── run.ps1                # Batch automation script
```

---

## 🇹🇷 Türkçe Özet

**SpotVault**, popüler açık kaynaklı **spotDL** motoru üzerine inşa edilmiş taşınabilir bir toplu Spotify arşivleme aracıdır.

* **Sıfır Manuel Kurulum:** spotDL'in arka plandaki Python çalışma ortamı doğrudan taşınabilir `.exe` içine gömülüdür; FFmpeg ise yerel olarak yönetilir. Sisteminize elle Python kurmanız veya PATH değişkenleriyle uğraşmanız gerekmez.
* **Bot Engeli Koruması:** Akış servislerinin bot engellerini aşan istemci ayarları hazır gelir.
* **Yalnızca Resmi Kaynak:** `--only-verified-results` filtresi sayesinde amatör videoları eler, sadece plak şirketlerinin resmi stüdyo kayıtlarını indirir.
* **Toplu Klasörleme:** `playlists.txt` içine eklenen tüm listeleri sırayla `Downloads/<Liste_Adı>/` klasörlerine 320 kbps MP3 olarak kaydeder.
* **Kullanım:** `playlists.txt` dosyasına linkleri yapıştırın ve **`start.bat`** dosyasına çift tıklayın.

---

## 🙏 Credits & Acknowledgments

SpotVault is built upon and inspired by the following open-source project:
* **[spotDL](https://github.com/spotDL/spotify-downloader)** — The core music metadata matching and downloading engine.

---

## ⚖️ Disclaimer

This tool is intended strictly for personal backup, research, and educational purposes. SpotVault does not host copyrighted files. Users are responsible for complying with local laws and terms of service.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.
