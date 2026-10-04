"""
Internationalization (i18n) module for SpotVault Desktop.
Supports full Turkish (TR) and English (EN) localization across all UI elements,
dialogs, status indicators, and background process notifications.
"""

from typing import Any, Dict

DEFAULT_LANGUAGE = "tr"
SUPPORTED_LANGUAGES = {"tr", "en"}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "tr": {
        # Header & Window
        "app_title": "SpotVault v1.0.0 — Offline Music & Android Sync",
        "app_header_title": "SpotVault v1.0.0",
        "app_subtitle": "Spotify Çevrimdışı Arşivleyici & Android ADB Eşzamanlama Stüdyosu",
        "lang_selector_label": "🌐 Dil:",
        # Settings Card
        "card_settings_title": " İndirme ve Format Ayarları ",
        "lbl_format": "Ses Formatı ve Kalite:",
        "lbl_storage": "Klasör ve Depolama Mimarisi:",
        "radio_standalone": "Her Playlist Ayrı Klasör (Bağımsız M3U8)",
        "radio_pool": "Tek Müzik Havuzu (Merkezi M3U8)",
        "chk_artwork": "Albüm Kapak Resmini Dosyaya Göm",
        "chk_metadata": "ID3 / Sanatçı Meta Etiketlerini Göm",
        "chk_lyrics": "Senkronize Şarkı Sözlerini (.lrc) İndir",
        # ADB Card
        "card_adb_title": " Android ADB Eşzamanlama ",
        "adb_disconnected": " Cihaz Bağlı Değil ",
        "adb_connected": " 🟢 Bağlı: {device} ",
        "adb_multiple": " 🟢 Çoklu Cihaz: {count} ",
        "btn_adb_refresh": "Yenile",
        "btn_adb_guide": "ℹ Nasıl Bağlarım? (USB Hata Ayıklama Rehberi)",
        "btn_adb_push": "📲 Telefona Aktar (ADB Push & Index)",
        "btn_adb_push_active": "⏳ Aktarılıyor...",
        # Download Card
        "lbl_urls": "Spotify Playlist veya Albüm Linkleri (Her satıra bir link):",
        "btn_download": "🚀 İndirmeyi Başlat (Akıllı Eşleştirici Aktif)",
        "btn_download_active": "⏳ İndiriliyor...",
        "btn_cancel": "⏹ İptal Et",
        "btn_cancel_active": "⏳ İptal Ediliyor...",
        "btn_regenerate_m3u": "🎵 Playlistleri Yenile (M3U8)",
        "btn_regenerate_m3u_active": "⏳ Yenileniyor...",
        # Console Card
        "lbl_terminal": "Canlı İşlem Terminali",
        "btn_clear_terminal": "Temizle",
        # Guide Dialog
        "guide_window_title": "Android USB Hata Ayıklama Rehberi",
        "guide_heading": "Android Cihazınızı USB ile Bağlama Adımları",
        "guide_content": (
            "1. Android cihazınızda 'Ayarlar' > 'Telefon Hakkında' bölümüne gidin.\n\n"
            "2. 'Yapım Numarası' (Build Number) seçeneğine 7 kez arka arkaya dokunarak 'Geliştirici Seçenekleri'ni aktif edin.\n\n"
            "3. 'Ayarlar' > 'Sistem' > 'Geliştirici Seçenekleri' (veya Ek Ayarlar) menüsüne girin.\n\n"
            "4. 'USB Hata Ayıklama' (USB Debugging) anahtarını açın.\n\n"
            "5. Cihazınızı USB kablosu ile bilgisayara bağlayın.\n\n"
            "6. Telefon ekranında beliren 'Bu bilgisayara her zaman izin ver' uyarısını onaylayın.\n\n"
            "7. SpotVault ekranındaki 'Yenile' butonuna tıklayarak cihazınızın algılandığını doğrulayın."
        ),
        "btn_guide_close": "Anladım",
        # Dialogs & Statuses
        "title_info": "Bilgi",
        "title_warning": "Uyarı",
        "title_error": "Hata",
        "title_success": "Tamamlandı",
        "msg_no_urls": "Lütfen indirmek için en az bir geçerli Spotify bağlantısı girin.",
        "msg_already_downloading": "Şu anda devam eden bir indirme işlemi var.",
        "msg_cancel_sent": "İptal isteği iletildi. Mevcut şarkı tamamlandıktan sonra duracak.",
        "msg_download_complete": "Tüm parçalar ve çalma listeleri başarıyla arşivlendi.",
        "msg_download_error": "İndirme işlemi sırasında hata oluştu:\n{error}",
        "msg_playlists_regenerated": "{count} adet çalma listesi (M3U8) başarıyla yenilendi.",
        "msg_no_playlists_found": "Yenilenecek çalma listesi veya müzik dosyası bulunamadı. Lütfen önce müzik indirin.",
        "msg_playlists_error": "Playlist yenileme hatası:\n{error}",
        "msg_sync_in_progress": "Aktarım zaten devam ediyor.",
        "msg_downloads_dir_missing": "İndirilenler klasörü bulunamadı: {path}",
        "msg_no_device_found": "Bağlı Android cihaz bulunamadı. Lütfen USB hata ayıklamayı açıp tekrar deneyin.",
        "msg_sync_success": "Müzikler Android cihazınıza başarıyla aktarıldı ve MediaScanner ile taratıldı.",
        "msg_sync_error": "Telefona aktarım sırasında hata oluştu:\n{error}",
        # Logs
        "log_start_download": "=== SpotVault İndirme İşlemi Başladı ({count} Liste) ===",
        "log_download_cancelled": "[INFO] İndirme kullanıcı tarafından iptal edildi.",
        "log_download_item": "--- [{index}/{total}] İndiriliyor: {url} ---",
        "log_playlists_updating": "=== Tüm İndirmeler Tamamlandı. Playlistler Oluşturuluyor... ===",
        "log_playlists_updated": "[PLAYLIST] {count} adet UTF-8 M3U8 çalma listesi güncellendi.",
        "log_no_playlists_created": "[PLAYLIST] Henüz indirilmiş müzik veya klasör bulunamadı.",
        "log_adb_push_start": "=== Android ADB Aktarımı Başlatıldı ===",
        "log_adb_device": "Hedef Cihaz: {device}",
        "log_adb_push_complete": "=== ADB Aktarımı Başarıyla Tamamlandı ===",
        "log_adb_push_error": "[ADB HATA] Aktarım başarısız: {error}",
    },
    "en": {
        # Header & Window
        "app_title": "SpotVault v1.0.0 — Offline Music & Android Sync",
        "app_header_title": "SpotVault v1.0.0",
        "app_subtitle": "Spotify Offline Archiver & Android ADB Sync Studio",
        "lang_selector_label": "🌐 Language:",
        # Settings Card
        "card_settings_title": " Download & Format Settings ",
        "lbl_format": "Audio Format & Quality:",
        "lbl_storage": "Folder & Storage Architecture:",
        "radio_standalone": "Separate Folder per Playlist (Standalone M3U8)",
        "radio_pool": "Unified Music Pool (Central M3U8)",
        "chk_artwork": "Embed Album Artwork into File",
        "chk_metadata": "Embed ID3 / Artist Metadata Tags",
        "chk_lyrics": "Download Synced Lyrics (.lrc)",
        # ADB Card
        "card_adb_title": " Android ADB Synchronization ",
        "adb_disconnected": " Device Not Connected ",
        "adb_connected": " 🟢 Connected: {device} ",
        "adb_multiple": " 🟢 Multiple Devices: {count} ",
        "btn_adb_refresh": "Refresh",
        "btn_adb_guide": "ℹ How to Connect? (USB Debugging Guide)",
        "btn_adb_push": "📲 Push to Phone (ADB Push & Index)",
        "btn_adb_push_active": "⏳ Syncing...",
        # Download Card
        "lbl_urls": "Spotify Playlist or Album Links (One link per line):",
        "btn_download": "🚀 Start Download (Smart Matcher Active)",
        "btn_download_active": "⏳ Downloading...",
        "btn_cancel": "⏹ Cancel",
        "btn_cancel_active": "⏳ Cancelling...",
        "btn_regenerate_m3u": "🎵 Refresh Playlists (M3U8)",
        "btn_regenerate_m3u_active": "⏳ Refreshing...",
        # Console Card
        "lbl_terminal": "Live Process Terminal",
        "btn_clear_terminal": "Clear",
        # Guide Dialog
        "guide_window_title": "Android USB Debugging Guide",
        "guide_heading": "Steps to Connect Your Android Device via USB",
        "guide_content": (
            "1. On your Android device, go to 'Settings' > 'About Phone'.\n\n"
            "2. Tap 'Build Number' 7 times repeatedly to enable 'Developer Options'.\n\n"
            "3. Navigate to 'Settings' > 'System' > 'Developer Options' (or Additional Settings).\n\n"
            "4. Toggle on 'USB Debugging'.\n\n"
            "5. Connect your device to the computer using a USB cable.\n\n"
            "6. When prompted on your phone, check 'Always allow from this computer' and tap OK.\n\n"
            "7. Click the 'Refresh' button in SpotVault to verify the connection."
        ),
        "btn_guide_close": "Got it",
        # Dialogs & Statuses
        "title_info": "Information",
        "title_warning": "Warning",
        "title_error": "Error",
        "title_success": "Success",
        "msg_no_urls": "Please enter at least one valid Spotify URL to download.",
        "msg_already_downloading": "A download process is already running.",
        "msg_cancel_sent": "Cancellation requested. It will stop after the current song completes.",
        "msg_download_complete": "All tracks and playlists have been successfully archived.",
        "msg_download_error": "An error occurred during download:\n{error}",
        "msg_playlists_regenerated": "{count} playlist(s) (M3U8) successfully regenerated.",
        "msg_no_playlists_found": "No playlists or music files found to refresh. Please download music first.",
        "msg_playlists_error": "Playlist refresh error:\n{error}",
        "msg_sync_in_progress": "Transfer is already in progress.",
        "msg_downloads_dir_missing": "Downloads directory not found: {path}",
        "msg_no_device_found": "No connected Android device found. Please enable USB debugging and retry.",
        "msg_sync_success": "Music files successfully pushed to Android device and indexed by MediaScanner.",
        "msg_sync_error": "An error occurred during transfer to phone:\n{error}",
        # Logs
        "log_start_download": "=== SpotVault Download Started ({count} Queue) ===",
        "log_download_cancelled": "[INFO] Download cancelled by user.",
        "log_download_item": "--- [{index}/{total}] Downloading: {url} ---",
        "log_playlists_updating": "=== All Downloads Completed. Generating Playlists... ===",
        "log_playlists_updated": "[PLAYLIST] {count} UTF-8 M3U8 playlist(s) updated.",
        "log_no_playlists_created": "[PLAYLIST] No downloaded music or directories found yet.",
        "log_adb_push_start": "=== Android ADB Transfer Started ===",
        "log_adb_device": "Target Device: {device}",
        "log_adb_push_complete": "=== ADB Transfer Successfully Completed ===",
        "log_adb_push_error": "[ADB ERROR] Transfer failed: {error}",
    }
}


def get_text(key: str, lang: str = "tr", **kwargs: Any) -> str:
    """
    Retrieves translated text for a key in the given language.
    Falls back to Turkish (tr) if missing in target language, or returns key itself.
    Supports str.format substitutions via keyword arguments.
    """
    normalized_lang = lang.lower() if lang else "tr"
    if normalized_lang not in SUPPORTED_LANGUAGES:
        normalized_lang = "tr"

    lang_dict = TRANSLATIONS.get(normalized_lang, TRANSLATIONS["tr"])
    text = lang_dict.get(key)
    if text is None:
        text = TRANSLATIONS["tr"].get(key, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
