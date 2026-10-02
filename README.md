# 🎵 SpotVault

> **Automated, Zero-Setup Spotify Playlist Archiving Pipeline**  
> *Download multiple Spotify playlists in verified 320 kbps MP3 with embedded high-resolution artwork and complete ID3 tags — with zero system installation.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows)](start.bat)
[![Python Required](https://img.shields.io/badge/Python-Not%20Required-success.svg)](#features)
[![Audio Quality](https://img.shields.io/badge/Quality-320%20kbps%20MP3-brightgreen.svg)](#why-spotvault)
[![Bypass](https://img.shields.io/badge/YouTube%20403-Bypassed-success.svg)](#key-features)

---

## ⚡ Why SpotVault?

Downloading Spotify playlists at scale has become increasingly frustrating in 2026:
* **Zotify & OnTheSpot:** Spotify closed the `librespot` protocol and revoked audio keys for free accounts (`BadCredentials` / `NoneType access_token`).
* **SpotiFLAC & Lucida:** Public community server pools frequently hit rate limits (*"The server is taking a scheduled short break. Please try again in 50 minutes"*).
* **Vanilla spotDL:** Throws `HTTP Error 403: Forbidden` due to YouTube's strict desktop bot detection, and can occasionally match amateur fan recordings, lyric videos, or concert clips.

**SpotVault** solves all of these problems in a **self-contained, portable Windows pipeline**.

---

## 🚀 Key Features

* **🛡️ YouTube 403 Bot-Bypass:** Uses built-in Android client player emulation (`--extractor-args youtube:player_client=android`) to completely avoid YouTube's bot detection.
* **💎 Official Music Guarantee (`--only-verified-results`):** Strictly enforces downloads from verified distributor audio (YouTube Music *Topic* channels, Sony, Universal, Warner, VEVO). Fan re-uploads, live concert phone recordings, and modified audio are rejected.
* **📁 Multi-Playlist Batch Automation:** Feed 1 or 100 playlists into `playlists.txt`. SpotVault automatically creates dedicated folders for each playlist under `Downloads/<Playlist_Name>/`.
* **🎨 Embedded Spotify Artwork & Full ID3 Tags:** Pulls 640x640 original cover art, artist names, album title, release year, and track numbering directly from Spotify and embeds them into each MP3.
* **⚡ Zero-Setup & 100% Portable:** No Python, no Node.js, and no system-wide FFmpeg installation required. Your Windows system PATH and registry remain untouched.
* **🔄 Smart Resume:** Safely interrupt and restart anytime. Previously downloaded tracks are automatically detected and skipped.

---

## 📊 Tool Comparison

| Feature | Vanilla spotDL | Zotify / OnTheSpot | SpotiFLAC | **SpotVault** |
| :--- | :---: | :---: | :---: | :---: |
| **Free Spotify Account Support** | Yes | ❌ Blocked | Yes | **✅ Yes (Zero Account Needed)** |
| **YouTube 403 Bot Blocks** | ❌ Fails (403) | N/A | N/A | **✅ Bypassed (Android Emulation)** |
| **Official Topic Audio Only** | ⚠️ Optional / Manual | N/A | Yes | **✅ Enforced (`--only-verified-results`)** |
| **Mass Batch Playlists (80+)** | ⚠️ Manual CLI | ❌ Rate-limited | ❌ 50 min wait | **✅ 100% Automated Queue** |
| **Auto Per-Playlist Folders** | ⚠️ Manual flag | Manual | Manual | **✅ Automatic (`Downloads/{list-name}`)** |
| **System Installation Required** | Python + FFmpeg | Python + PyQt | None | **✅ Portable (Zero System Install)** |

---

## 📦 Project Structure

```text
spotvault/
├── start.bat                  # One-click Windows launcher
├── playlists.example.txt      # Template for Spotify playlist URLs
├── playlists.txt              # Your active playlist queue (git-ignored)
├── LICENSE                    # MIT License
├── README.md                  # Documentation
└── core/                      # Portable engine & automation
    ├── spotdl.exe             # Standalone downloader engine (v4.5.2)
    └── run.ps1                # Hardened PowerShell batch pipeline
```

---

## 🛠️ Quick Start

### 1. Clone or Download
```bash
git clone https://github.com/your-username/spotvault.git
cd spotvault
```

### 2. Add Your Playlists
1. Copy `playlists.example.txt` to `playlists.txt` (or let `start.bat` create it for you).
2. Open `playlists.txt` and paste your Spotify playlist, album, or track links (one per line):
   ```text
   https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd
   ```

### 3. Launch
Simply **double-click `start.bat`**.

All tracks will be neatly organized into:
```text
Downloads/
├── Today's Top Hits/
│   ├── Dua Lipa - Houdini.mp3
│   └── ...
└── RapCaviar/
    ├── Kendrick Lamar - Not Like Us.mp3
    └── ...
```

---

## 🇹🇷 Türkçe Kullanım Kılavuzu

### Neden SpotVault?
Mevcut Spotify indirme araçlarının neredeyse tamamı 2026 yılı itibarıyla ya hesap kısıtlamalarına takılmakta (`Zotify`), ya sunucu kotaları yüzünden bekletmekte (`SpotiFLAC`), ya da YouTube'un bot korumasına çarpıp `403 Forbidden` hatası vermektedir (`ham spotDL`).

**SpotVault**, taşınabilir bir mimari üzerinde:
1. **YouTube Bot Korumasını Aşar:** Android istemci emülasyonu ile `403 Forbidden` hatasını kökten engeller.
2. **Resmi Sanatçı Kaydı Garantisi:** `--only-verified-results` filtresi ile amatör kullanıcı videolarını eler, yalnızca plak şirketlerinin lisanslı stüdyo kayıtlarını indirir.
3. **80+ Playlist Otomasyonu:** Linkleri sırayla okur, her çalma listesi için `Downloads/<Liste_Adı>/` klasörü açar.
4. **Orijinal Kapak & Künye:** Spotify'daki 640x640 orijinal kapak resmini ve ID3 etiketlerini MP3 dosyasına gömer.
5. **Sıfır Kurulum:** Bilgisayara Python veya FFmpeg kurmanız gerekmez.

### Nasıl Kullanılır?
1. `playlists.example.txt` dosyasını `playlists.txt` olarak kopyalayın.
2. İndirmek istediğiniz Spotify çalma listesi linklerini alt alta yapıştırın.
3. **`start.bat`** dosyasına çift tıklayın!

---

## ⚖️ Disclaimer

This tool is intended strictly for personal backup, research, and educational purposes. SpotVault does not bypass DRM or host copyrighted audio. Audio is sourced from publicly available official distributor streams under fair use principles. Users are solely responsible for compliance with local copyright laws and streaming services' terms of service.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
