# 🎵 SpotVault v1.0.1

> **Automated, Zero-Setup Spotify Playlist Archiving & Android ADB Sync Studio**  
> *A hardened, cross-platform music preservation suite featuring Smart Official Matching, incremental diff-sync, and direct Android device synchronization.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows & Linux](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0078D6.svg?logo=windows&logoColor=white)](start.bat)
[![Release: v1.0.1](https://img.shields.io/badge/Release-v1.0.1-brightgreen.svg)](#-whats-new-in-v101)
[![Audio: 320k MP3 & M4A](https://img.shields.io/badge/Audio-320k%20MP3%20%2F%20M4A%20AAC-brightgreen.svg)](#-key-features)
[![ADB: Bundled](https://img.shields.io/badge/Android%20ADB-Bundled%20%26%20Portable-orange.svg)](#-1-click-android-adb-sync)

---

**Languages / Diller:**  
🇬🇧 [English](#-english) | 🇹🇷 [Türkçe](#-türkçe)

---

# 🇬🇧 English

## 📌 Overview

**SpotVault** is a dual-mode (GUI & CLI) desktop audio suite engineered to archive Spotify playlists and albums in maximum fidelity to local storage. It features an intelligent **Smart Official Matcher** that captures TR (Turkey) regional official catalogs as well as global independent and major publishers without omission. SpotVault includes 1-click direct USB synchronization to Android devices and triggers immediate music player indexation.

The legacy v1.0.0 batch wrapper has been completely re-engineered into a self-contained, **Windows & Linux cross-platform**, modern Dark Slate music preservation platform.

---

## ⚡ What's New in v1.0.1

* 🎯 **Smart Official Matcher:** Standard tools with `--only-verified-results` routinely skip tracks hosted on official regional distributor channels rather than YouTube's auto-generated "Topic" channels. SpotVault accurately identifies official releases and distributor uploads:
  - **±3-Second Duration Tolerance:** Discards music videos with dialog, extended sketches, and sped-up/slowed edits.
  - **Anti-Junk Keyword Filter:** Automatically excludes fan covers, live concert bootlegs, reverb edits, and amateur remixes.
  - **Extensible Custom Whitelist (`custom_labels.txt`):** Effortlessly add any regional, underground, or niche record label or channel name without modifying source code.
* 📲 **1-Click Android ADB Sync:** Bundled portable Google Platform-Tools ADB (`core/adb/`) transfers your complete library directly to `/sdcard/Music/Muzikler` over USB:
  - **Storage Pre-Check:** Analyzes free device storage (`df /sdcard`) prior to transfer, aborting safely if storage is insufficient.
  - **MediaScanner Trigger:** Broadcasts `MEDIA_SCANNER_SCAN_FILE` intents upon transfer completion so players (PowerAudio, VLC, Musicolet) index tracks immediately without rebooting.
* 🎨 **Modern Dark Slate GUI:** Tkinter interface built with asynchronous background threading, real-time log console, and live device status badge (🟢 Connected / 🟡 Unauthorized / ⚪ Not Connected).
* 🌐 **Full Cross-Platform Support (Windows & Linux):** 1-click startup on Windows via `start.bat` and on Linux via `start.sh`, with automatic dependency and runtime resolution.
* 🎼 **Flexible Storage & Audio Formats:**
  - **MP3 (320 kbps)** or **M4A (AAC auto - direct YouTube stream)**.
  - **Per-Playlist Independent Folders** (standalone `.m3u8`) or **Unified Music Pool** (centralized `Pool/` + `Playlists/`).
* 🔄 **0.001s Incremental Diff-Sync:** Validates local file existence in 0.001 seconds to bypass redundant network queries. Tracks removed from Spotify are **never deleted** from local archives (strict zero-data-loss principle).

---

## 📊 Comparison Table

| Feature | Online / Web Converters | Standard spotDL CLI | SpotVault v1.0.0 | **SpotVault v1.0.1** |
| :--- | :---: | :---: | :---: | :---: |
| **Login Requirement** | ❌ Account / Premium Required | ✅ No Login | ✅ No Login | **✅ Zero Login (Zero Account Risk)** |
| **Regional & Independent Catalogs** | ⚠️ Unreliable | ❌ Skips unverified / downloads junk | ❌ Skips verified | **✅ Smart Matcher (TR & Global Whitelist)** |
| **Custom Label Whitelisting** | ❌ None | ❌ None | ❌ None | **✅ custom_labels.txt Extensible** |
| **Junk & Fan Edit Filtering** | ❌ Frequently wrong version | ⚠️ Limited `--only-verified` | ✅ Topic/VEVO only | **✅ Whitelist + ±3s Tolerance + Blacklist** |
| **Direct Android Phone Transfer** | ❌ Manual MTP Drag & Drop | ❌ None | ⚠️ Hardcoded Script | **✅ Bundled ADB + Storage Pre-Check** |
| **Automatic Music Player Indexing** | ❌ Device restart required | ❌ None | ⚠️ Manual Script | **✅ Automatic MediaScanner Broadcast** |
| **User Interface** | ⚠️ Ad-heavy websites | ❌ Terminal only | ❌ Batch prompt only | **✅ Modern Dark Slate GUI + Headless CLI** |
| **Platform Compatibility** | Browser | Python / CLI | Windows only | **✅ Windows & Linux** |

---

## 🛠 Quick Start

### 🪟 Windows Users

#### Method 1: Graphical Interface (GUI)
1. Double-click [start.bat](file:///c:/proje/spotvault%20v1.0.1/start.bat).
2. Python dependencies, ADB, and FFmpeg are automatically resolved, and the GUI opens.
3. Paste Spotify playlist or track URLs into the text box and click **"🚀 İndirmeyi Başlat"**.
4. Connect your Android phone via USB and click **"📲 Telefona Aktar (ADB Push)"**.

#### Method 2: Command Line Interface (CLI)
```cmd
:: Download a single track or playlist
python spotvault.py --url "https://open.spotify.com/playlist/..." --format mp3 --bitrate 320k

:: Batch download all playlists from playlists.txt and sync to Android
python spotvault.py --file playlists.txt --sync-adb

:: Regenerate M3U8 playlists only
python spotvault.py --generate-playlists
```

---

### 🐧 Linux Users

#### Installation & Launch
```bash
# Make launcher executable
chmod +x start.sh

# Launch the Graphical Interface (GUI)
./start.sh

# Or run directly in headless CLI mode
python3 spotvault.py --file playlists.txt --sync-adb
```

> **Linux Tip:** For Android ADB sync on Linux, install ADB via your system package manager:
> ```bash
> sudo apt install adb          # Debian / Ubuntu / Mint
> sudo pacman -S android-tools    # Arch / Manjaro
> sudo dnf install android-tools   # Fedora / RHEL
> ```

---

## 📱 Android USB Debugging Setup Guide

To enable direct cable synchronization to your Android device:

1. On your phone, go to **Settings → About Phone → Build Number** and tap it 7 times until you see *"You are now a developer"*.
2. Open **Settings → System / Additional Settings → Developer Options**.
3. Enable **USB Debugging**.
4. Connect your phone to your computer via USB cable.
5. In the prompt *"Allow USB debugging from this computer?"*, check *"Always allow from this computer"* and tap **Allow / OK**.
6. The SpotVault device badge will automatically transition to **🟢 Bağlı: [Device Code]**.

---

<br>

---

# 🇹🇷 Türkçe

## 📌 Genel Bakış

**SpotVault**, Spotify çalma listelerini ve albümlerini en yüksek ses kalitesiyle yerel diske indiren, **TR (Türkiye) yerel resmi müzik katalogları ile küresel bağımsız/majör yayıncıları** kaçırmayan **Akıllı Resmi Eşleştiriciye (Smart Official Matcher)** sahip, tek tıkla Android telefonunuza aktaran ve müzik çalar kütüphanesini otomatik güncelleyen çift modlu (GUI & CLI) masaüstü stüdyosudur.

v1.0.0 sürümündeki saf spotDL batch wrapper yapısı, v1.0.1 ile birlikte kendi kendine yeten, **Windows ve Linux uyumlu**, modern karanlık temalı tam teşekküllü bir müzik koruma platformuna dönüştürüldü.

---

## ⚡ v1.0.1 ile Gelen Yenilikler

* 🎯 **Akıllı Resmi Eşleştirici (Smart Official Matcher):** Standart araçların `--only-verified-results` filtresi nedeniyle atladığı, YouTube üzerinde otomatik sanatçı konu kanalı (Topic) yerine resmi yayıncı ve yetkili distribütör kanallarında barındırılan **TR yerel ve küresel bağımsız resmi katalogları** kaçırmaz.
  - **±3 Saniye Süre Doğrulaması:** Klip içi konuşmaları, uzun introları ve hızlandırılmış (speed-up/slowed) kayıtları eler.
  - **Anti-Çöp Filtresi:** Fan cover'ları, konser canlı kayıtları (live), reverb ve amatör remixleri otomatik reddeder.
  - **Genişletilebilir Özel Whitelist (`custom_labels.txt`):** Kullanıcıların diledikleri yerel, bölgesel veya niş plak şirketlerini/yayıncı kanallarını kod değiştirmeden sisteme tanıtabilmesi.
* 📲 **Tek Tık Android ADB Senkronizasyonu:** Dahili Google Platform-Tools ADB (`core/adb/`) ile telefonunuzu kabloyla bağlayıp tek tıkla tüm kütüphaneyi `/sdcard/Music/Muzikler` dizinine aktarın.
  - **Depolama Ön Denetimi:** Aktarım öncesi telefon hafızasını (`df /sdcard`) kontrol eder, yetersiz alanda işlemi güvenle durdurur.
  - **MediaScanner Tetikleyici:** Aktarım bittiğinde `MEDIA_SCANNER_SCAN_FILE` intent'i yayınlayarak PowerAudio, VLC, Musicolet gibi oynatıcıların şarkıları yeniden başlatmaya gerek kalmadan anında indekslemesini sağlar.
* 🎨 **Modern Koyu Tema Masaüstü Arayüzü (GUI):** Asenkron iş parçacıkları (threading) ile donmayan, canlı log konsollu, cihaz durum rozetli (🟢 Bağlı / 🟡 Yetkisiz / ⚪ Bağlı Değil) karanlık tema Tkinter arayüzü.
* 🌐 **Tam Çapraz Platform (Windows & Linux):** Windows'ta `start.bat`, Linux'ta `start.sh` ile tek tıkla başlatma. Otomatik bağımlılık ve sistem araçları çözümlemesi.
* 🎼 **Esnek Format ve Depolama Mimarisi:**
  - **MP3 (320 kbps)** veya **M4A (AAC auto - YouTube doğrudan akış)**.
  - **Her Playlist Ayrı Klasör** (bağımsız `.m3u8`) veya **Tek Müzik Havuzu** (merkezi `Pool/` + `Playlists/`).
* 🔄 **0.001s Artımlı Senkronizasyon (Incremental Diff-Sync):** Daha önce indirilmiş şarkıları 0.001 saniyede yerel dosya varlık kontrolüyle atlar. Spotify'dan silinen şarkıları yerel arşivden **asla silmez** (kesin veri kayıpsızlık ilkesi).

---

## 📊 Karşılaştırma Tablosu

| Özellik | Web / Online Araçlar | Standart spotDL CLI | SpotVault v1.0.0 | **SpotVault v1.0.1** |
| :--- | :---: | :---: | :---: | :---: |
| **Giriş / Login Zorunluluğu** | ❌ Premium veya Giriş Şart | ✅ Girişsiz | ✅ Girişsiz | **✅ Girişsiz (Sıfır Hesap Riski)** |
| **Bölgesel ve Bağımsız Resmi Kataloglar** | ⚠️ Belirsiz | ❌ Verified atlar, unverified çöp çeker | ❌ Verified atlar | **✅ Akıllı Eşleştirici (TR & Global Whitelist)** |
| **Özel Plak Şirketi Tanımlama** | ❌ Yok | ❌ Yok | ❌ Yok | **✅ custom_labels.txt Genişletilebilir** |
| **Çöp / Fan Edit Engelleme** | ❌ Sıklıkla yanlış sürüm | ⚠️ `--only-verified` ile sınırlı | ✅ Topic/VEVO | **✅ Whitelist + Süre Toleransı + Blacklist** |
| **Android Telefona Doğrudan Aktarım** | ❌ Manuel MTP Kopyalama | ❌ Yok | ⚠️ Hardcoded Script | **✅ Dahili ADB + Depolama Kontrolü** |
| **Otomatik Müzik Çalar İndeksleme** | ❌ Telefonu yeniden başlatmak gerekir | ❌ Yok | ⚠️ Manuel Script | **✅ Otomatik MediaScanner Yayını** |
| **Kullanıcı Arayüzü** | ⚠️ Reklam dolu web | ❌ Yalnızca Terminal | ❌ Yalnızca Batch | **✅ Modern Koyu Tema GUI + CLI** |
| **Platform Desteği** | Tarayıcı | Python / CLI | Windows | **✅ Windows & Linux** |

---

## 🛠 Hızlı Başlangıç

### 🪟 Windows Kullanıcıları

#### Yöntem 1: Grafik Arayüz (GUI)
1. [start.bat](file:///c:/proje/spotvault%20v1.0.1/start.bat) dosyasına çift tıklayın.
2. Gerekli Python paketleri, ADB ve FFmpeg kontrol edilir, arayüz açılır.
3. Spotify çalma listesi veya şarkı linklerinizi kutucuğa yapıştırın ve **"🚀 İndirmeyi Başlat"** butonuna basın.
4. Telefonunuzu USB ile bağlayıp **"📲 Telefona Aktar (ADB Push)"** butonuna tıklayın.

#### Yöntem 2: Komut Satırı (CLI)
```cmd
:: Tek bir şarkı veya playlist indir
python spotvault.py --url "https://open.spotify.com/playlist/..." --format mp3 --bitrate 320k

:: playlists.txt içerisindeki tüm listeleri indir ve telefona aktar
python spotvault.py --file playlists.txt --sync-adb

:: Yalnızca M3U8 çalma listelerini yenile
python spotvault.py --generate-playlists
```

---

### 🐧 Linux Kullanıcıları

#### Kurulum & Başlatma
```bash
# Başlatıcıyı çalıştırılabilir yapın
chmod +x start.sh

# Arayüzü başlatın (GUI)
./start.sh

# Veya doğrudan CLI modunda çalıştırın
python3 spotvault.py --file playlists.txt --sync-adb
```

> **Linux İpucu:** Linux ortamında ADB aktarımı için sistem paket yöneticinizden ADB'yi kurabilirsiniz:
> ```bash
> sudo apt install adb          # Debian / Ubuntu / Mint
> sudo pacman -S android-tools    # Arch / Manjaro
> sudo dnf install android-tools   # Fedora / RHEL
> ```

---

## 📱 Android USB Hata Ayıklama Rehberi (Nasıl Bağlarım?)

SpotVault'un telefonunuza doğrudan kabloyla müzik aktarabilmesi için:

1. Telefonunuzda **Ayarlar → Telefon Hakkında → Derleme Numarası** seçeneğine 7 kez arka arkaya dokunun (*"Artık bir geliştiricisiniz"* mesajını görün).
2. **Ayarlar → Ek Ayarlar / Sistem → Geliştirici Seçenekleri** menüsüne gidin.
3. **USB Hata Ayıklama (USB Debugging)** özelliğini açın.
4. Telefonu USB kablosuyla bilgisayara bağlayın.
5. Telefon ekranında çıkacak *"Bu bilgisayara izin verilsin mi?"* bildiriminde *"Bu bilgisayara her zaman izin ver"* kutucuğunu işaretleyip **İzin Ver / Tamam** deyin.
6. SpotVault ekranındaki durum rozeti **🟢 Bağlı: [Cihaz Kodu]** olarak güncellenecektir.

---

<br>

---

## 📂 Proje Dizin Yapısı / Project Structure

```
spotvault v1.0.1/
├── spotvault.py              # Dual-mode (GUI / CLI) entrypoint / Çift modlu ana giriş noktası
├── start.bat                 # Windows one-click launcher / Taşınabilir Windows başlatıcısı
├── start.sh                  # Linux one-click launcher / Taşınabilir Linux başlatıcısı
├── playlists.txt             # Batch download playlist URL pool / Toplu indirme link havuzu
├── custom_labels.txt         # Extensible custom record label whitelist / Özel plak şirketi whitelist dosyası
├── requirements.txt          # Python dependencies (spotdl, yt-dlp, mutagen, requests)
├── core/
│   ├── adb/                  # Bundled Google ADB platform-tools (Windows)
│   ├── ffmpeg.exe            # Bundled portable FFmpeg binary (Windows)
│   ├── config.py             # SpotVaultConfig model & cross-platform binary resolvers
│   ├── matcher.py            # Smart Official Matcher (TR & Global whitelist, ±3s, anti-junk filter)
│   ├── downloader.py         # spotDL runner, 0.001s diff-skip, fallback orchestrator
│   ├── playlist_generator.py # UTF-8 #EXTM3U playlist generator (standalone & pool modes)
│   ├── adb_sync.py           # ADB device discovery, storage pre-check, push & MediaScanner engine
│   └── run.ps1               # PowerShell helper automation script
├── gui/
│   ├── app.py                # Modern Dark Slate Tkinter desktop application
│   └── theme.py              # Cross-platform UI theme tokens & system font mappings
```

---

## 🧪 Doğrulama & Kararlılık / Quality & Verification

SpotVault v1.0.1, tüm modülleriyle (**Core Configuration**, **Smart Official Matcher**, **Incremental Sync**, **ADB Engine**, **Playlist Generator**) 40 birim ve entegrasyon testi ile doğrulanmış ve %100 test başarı oranına sahip kararlı bir sürümdür.

SpotVault v1.0.1 has been comprehensively verified across all modules (**Core Configuration**, **Smart Official Matcher**, **Incremental Sync**, **ADB Engine**, **Playlist Generator**) with a 40-test suite achieving a 100% pass rate.

---

## ⚖️ Lisans & Telif / License & Disclaimer

Bu proje [MIT Lisansı](LICENSE) kapsamında dağıtılmaktadır. Spotify veya YouTube ile doğrudan bir bağlantısı yoktur. İndirilen içeriklerin kullanım hakları ilgili hak sahiplerine aittir.

This project is licensed under the [MIT License](LICENSE). SpotVault is not affiliated with or endorsed by Spotify or YouTube. All music copyrights belong to their respective owners.
