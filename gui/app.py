import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional

from core.adb_sync import AdbSyncEngine
from core.config import SpotVaultConfig
from core.downloader import SpotVaultDownloader
from core.playlist_generator import generate_all_playlists
from gui.theme import (
    ACCENT_PRIMARY,
    ACCENT_SPOTIFY,
    BG_CARD,
    BG_INPUT,
    BG_MAIN,
    BG_SURFACE,
    BORDER_COLOR,
    FONT_BODY,
    FONT_CONSOLE,
    FONT_HEADING,
    FONT_SUBTITLE,
    FONT_TITLE,
    STATUS_ERROR,
    STATUS_SUCCESS,
    STATUS_WARNING,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY
)


class SpotVaultApp(tk.Tk):
    """
    Main desktop window and UI controller for SpotVault v1.0.1.
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initializes window layout, state models, asynchronous workers, and visual widgets.
        """
        super().__init__()

        self.title("SpotVault v1.0.1 — Offline Music & Android Sync")
        self.geometry("1080x720")
        self.minsize(960, 640)
        self.configure(bg=BG_MAIN)

        self.config_path = config_path or (Path(__file__).resolve().parent.parent / "spotvault_config.json")
        self.config = SpotVaultConfig.load(self.config_path)

        self.adb_engine = AdbSyncEngine(log_callback=self.log_message)
        self.log_queue: queue.Queue = queue.Queue()
        self.is_downloading = False
        self.is_syncing = False

        self._build_ui()
        self._load_saved_urls()
        self._start_log_consumer()
        self._start_device_monitor()

    def _build_ui(self) -> None:
        """
        Constructs header, left configuration sidebar, and right execution terminal.
        """
        header = tk.Frame(self, bg=BG_SURFACE, height=60, padx=20, pady=10)
        header.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header,
            text="SpotVault v1.0.1",
            font=FONT_TITLE,
            fg=ACCENT_SPOTIFY,
            bg=BG_SURFACE
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header,
            text="Spotify Çevrimdışı Arşivleyici & Android ADB Eşzamanlama Stüdyosu",
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        subtitle_label.pack(side=tk.LEFT, padx=15, pady=4)

        main_content = tk.Frame(self, bg=BG_MAIN, padx=15, pady=15)
        main_content.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(main_content, bg=BG_MAIN, width=380)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        right_panel = tk.Frame(main_content, bg=BG_MAIN)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_settings_card(left_panel)
        self._build_adb_card(left_panel)
        self._build_download_card(right_panel)
        self._build_log_console(right_panel)

    def _build_settings_card(self, parent: tk.Frame) -> None:
        """
        Creates format, bitrate, storage mode, and metadata option controls.
        """
        card = tk.LabelFrame(
            parent,
            text=" İndirme ve Format Ayarları ",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=FONT_SUBTITLE,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=(0, 10))

        fmt_label = tk.Label(card, text="Ses Formatı ve Kalite:", bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_HEADING)
        fmt_label.pack(anchor=tk.W, pady=(4, 2))

        self.format_var = tk.StringVar(value="MP3 (320 kbps)")
        fmt_dropdown = ttk.Combobox(
            card,
            textvariable=self.format_var,
            values=["MP3 (320 kbps)", "MP3 (192 kbps)", "M4A (AAC auto)"],
            state="readonly"
        )
        fmt_dropdown.pack(fill=tk.X, pady=(0, 8))
        fmt_dropdown.bind("<<ComboboxSelected>>", self._on_format_changed)

        mode_label = tk.Label(card, text="Klasör ve Depolama Mimarisi:", bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_HEADING)
        mode_label.pack(anchor=tk.W, pady=(4, 2))

        self.storage_var = tk.StringVar(value=self.config.storage_mode)
        rb_standalone = tk.Radiobutton(
            card,
            text="Her Playlist Ayrı Klasör (Bağımsız M3U8)",
            variable=self.storage_var,
            value="standalone",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._on_storage_mode_changed
        )
        rb_standalone.pack(anchor=tk.W)

        rb_pool = tk.Radiobutton(
            card,
            text="Tek Müzik Havuzu (Merkezi M3U8)",
            variable=self.storage_var,
            value="pool_m3u8",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._on_storage_mode_changed
        )
        rb_pool.pack(anchor=tk.W, pady=(0, 8))

        self.artwork_var = tk.BooleanVar(value=self.config.embed_artwork)
        cb_art = tk.Checkbutton(
            card,
            text="Albüm Kapak Resmini Dosyaya Göm",
            variable=self.artwork_var,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._save_config
        )
        cb_art.pack(anchor=tk.W)

        self.metadata_var = tk.BooleanVar(value=self.config.embed_metadata)
        cb_meta = tk.Checkbutton(
            card,
            text="ID3 / Sanatçı Meta Etiketlerini Göm",
            variable=self.metadata_var,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._save_config
        )
        cb_meta.pack(anchor=tk.W)

        self.lyrics_var = tk.BooleanVar(value=self.config.download_lyrics)
        cb_lyrics = tk.Checkbutton(
            card,
            text="Senkronize Şarkı Sözlerini (.lrc) İndir",
            variable=self.lyrics_var,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._save_config
        )
        cb_lyrics.pack(anchor=tk.W)

    def _build_adb_card(self, parent: tk.Frame) -> None:
        """
        Creates Android device status badge, connection guide popup, and ADB Push action button.
        """
        card = tk.LabelFrame(
            parent,
            text=" Android ADB Eşzamanlama ",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=FONT_SUBTITLE,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        card.pack(fill=tk.X)

        badge_row = tk.Frame(card, bg=BG_CARD)
        badge_row.pack(fill=tk.X, pady=(4, 8))

        self.device_badge = tk.Label(
            badge_row,
            text="⚪ Cihaz Aranıyor...",
            bg="#334155",
            fg=TEXT_PRIMARY,
            font=FONT_HEADING,
            padx=8,
            pady=4
        )
        self.device_badge.pack(side=tk.LEFT)

        btn_refresh = tk.Button(
            badge_row,
            text="Yenile",
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            command=self._refresh_device_status
        )
        btn_refresh.pack(side=tk.RIGHT)

        btn_guide = tk.Button(
            card,
            text="ℹ Nasıl Bağlarım? (USB Hata Ayıklama Rehberi)",
            bg=BG_CARD,
            fg=ACCENT_PRIMARY,
            relief=tk.FLAT,
            anchor=tk.W,
            command=self._show_adb_guide
        )
        btn_guide.pack(fill=tk.X, pady=(0, 8))

        self.btn_push = tk.Button(
            card,
            text="📲 Telefona Aktar (ADB Push & Index)",
            bg=ACCENT_PRIMARY,
            fg="#ffffff",
            font=FONT_HEADING,
            relief=tk.FLAT,
            pady=6,
            command=self._start_adb_push_thread
        )
        self.btn_push.pack(fill=tk.X, pady=(4, 0))

    def _build_download_card(self, parent: tk.Frame) -> None:
        """
        Creates URL entry panel and download control triggers.
        """
        card = tk.Frame(parent, bg=BG_MAIN)
        card.pack(fill=tk.X, pady=(0, 10))

        url_label = tk.Label(
            card,
            text="Spotify Playlist veya Albüm Linkleri (Her satıra bir link):",
            bg=BG_MAIN,
            fg=TEXT_PRIMARY,
            font=FONT_HEADING
        )
        url_label.pack(anchor=tk.W, pady=(0, 4))

        self.url_text = tk.Text(
            card,
            height=5,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            font=FONT_BODY,
            padx=8,
            pady=8
        )
        self.url_text.pack(fill=tk.X, pady=(0, 8))

        btn_bar = tk.Frame(card, bg=BG_MAIN)
        btn_bar.pack(fill=tk.X)

        self.btn_download = tk.Button(
            btn_bar,
            text="🚀 İndirmeyi Başlat (Akıllı Eşleştirici Aktif)",
            bg=ACCENT_SPOTIFY,
            fg="#ffffff",
            font=FONT_HEADING,
            relief=tk.FLAT,
            padx=16,
            pady=8,
            command=self._start_download_thread
        )
        self.btn_download.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        btn_gen_m3u = tk.Button(
            btn_bar,
            text="🎵 Playlistleri Yenile (M3U8)",
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=12,
            pady=8,
            command=self._regenerate_playlists
        )
        btn_gen_m3u.pack(side=tk.RIGHT)

    def _build_log_console(self, parent: tk.Frame) -> None:
        """
        Creates scrolling terminal text area for real-time operation output.
        """
        card = tk.LabelFrame(
            parent,
            text=" Canlı İşlem Terminali ",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=FONT_SUBTITLE,
            padx=10,
            pady=8,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True)

        self.console = tk.Text(
            card,
            bg="#030712",
            fg="#22c55e",
            font=FONT_CONSOLE,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=8,
            pady=8
        )
        scrollbar = tk.Scrollbar(card, command=self.console.yview)
        self.console.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def log_message(self, message: str) -> None:
        """
        Enqueues log message safely from worker threads.
        """
        self.log_queue.put(message)

    def _start_log_consumer(self) -> None:
        """
        Pulls queued log messages and appends them to the Tkinter console.
        """
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.console.insert(tk.END, f"{msg}\n")
            self.console.see(tk.END)
        self.after(100, self._start_log_consumer)

    def _start_device_monitor(self) -> None:
        """
        Polls connected Android devices periodically.
        """
        threading.Thread(target=self._query_device_state_async, daemon=True).start()
        self.after(4000, self._start_device_monitor)

    def _query_device_state_async(self) -> None:
        """
        Runs device status check on background thread to prevent UI freezing.
        """
        status = self.adb_engine.get_device_status()
        self.after(0, self._update_device_badge, status)

    def _update_device_badge(self, status: Dict[str, Any]) -> None:
        """
        Updates device status badge color and text.
        """
        state = status.get("state", "none")
        serial = status.get("serial", "")

        if state == "device":
            self.device_badge.config(
                text=f"🟢 Bağlı: {serial}",
                bg="#064e3b",
                fg="#a7f3d0"
            )
            self.btn_push.config(state=tk.NORMAL)
        elif state == "unauthorized":
            self.device_badge.config(
                text="🟡 Yetkisiz: Telefonda İzin Verin",
                bg="#78350f",
                fg="#fde68a"
            )
            self.btn_push.config(state=tk.DISABLED)
        else:
            self.device_badge.config(
                text="⚪ Cihaz Bağlı Değil",
                bg="#334155",
                fg=TEXT_SECONDARY
            )
            self.btn_push.config(state=tk.DISABLED)

    def _refresh_device_status(self) -> None:
        """
        Manually triggers an immediate device poll.
        """
        self.device_badge.config(text="⚪ Taranıyor...", bg="#334155", fg=TEXT_SECONDARY)
        threading.Thread(target=self._query_device_state_async, daemon=True).start()

    def _show_adb_guide(self) -> None:
        """
        Displays modal instructions on enabling USB debugging and trusting PC.
        """
        guide_text = (
            "1. Telefonunuzda Ayarlar -> Telefon Hakkında bölümüne gidin.\n"
            "2. 'Derleme Numarası' (Build Number) seçeneğine 7 kez arka arkaya dokunun.\n"
            "   (Artık bir geliştiricisiniz mesajı görünecektir).\n\n"
            "3. Ayarlar -> Ek Ayarlar -> Geliştirici Seçenekleri menüsüne girin.\n"
            "4. 'USB Hata Ayıklama' (USB Debugging) anahtarını açın.\n\n"
            "5. Telefonu USB kablosuyla bilgisayara bağlayın.\n"
            "6. Telefon ekranında 'Bu bilgisayara izin verilsin mi?' uyarısı çıktığında\n"
            "   'Bu bilgisayara her zaman izin ver' kutusunu işaretleyip 'Tamam' deyin.\n\n"
            "7. Ardından buradaki 'Yenile' butonuna tıklayın. Yeşil ışık yanacaktır."
        )
        messagebox.showinfo("Android USB Hata Ayıklama Rehberi", guide_text)

    def _on_format_changed(self, event: Optional[Any] = None) -> None:
        """
        Handles format dropdown selection and maps to configuration parameters.
        """
        choice = self.format_var.get()
        if "M4A" in choice:
            self.config.audio_format = "m4a"
            self.config.bitrate = "auto"
        elif "192" in choice:
            self.config.audio_format = "mp3"
            self.config.bitrate = "192k"
        else:
            self.config.audio_format = "mp3"
            self.config.bitrate = "320k"
        self._save_config()

    def _on_storage_mode_changed(self) -> None:
        """
        Updates storage architecture mode.
        """
        self.config.storage_mode = self.storage_var.get()
        self._save_config()

    def _save_config(self) -> None:
        """
        Saves updated GUI selections to disk.
        """
        self.config.embed_artwork = self.artwork_var.get()
        self.config.embed_metadata = self.metadata_var.get()
        self.config.download_lyrics = self.lyrics_var.get()
        self.config.save(self.config_path)

    def _load_saved_urls(self) -> None:
        """
        Populates URL box with playlists.txt if present.
        """
        playlists_file = Path(__file__).resolve().parent.parent / self.config.playlists_file
        if playlists_file.exists():
            try:
                content = playlists_file.read_text(encoding="utf-8")
                self.url_text.insert("1.0", content)
            except Exception:
                pass

    def _start_download_thread(self) -> None:
        """
        Validates input and launches background downloader execution.
        """
        if self.is_downloading:
            messagebox.showwarning("İşlem Devam Ediyor", "Şu anda devam eden bir indirme işlemi var.")
            return

        urls_raw = self.url_text.get("1.0", tk.END).strip()
        urls = [line.strip() for line in urls_raw.splitlines() if line.strip() and not line.startswith("#")]

        if not urls:
            messagebox.showwarning("Eksik URL", "Lütfen en az bir Spotify playlist veya albüm linki girin.")
            return

        self.is_downloading = True
        self.btn_download.config(state=tk.DISABLED, text="⏳ İndiriliyor...")
        threading.Thread(target=self._run_download_task, args=(urls,), daemon=True).start()

    def _run_download_task(self, urls: List[str]) -> None:
        """
        Executes download and fallback matcher pipeline across provided URLs.
        """
        self.log_message(f"=== SpotVault İndirme İşlemi Başladı ({len(urls)} Liste) ===")
        downloader = SpotVaultDownloader(self.config, log_callback=self.log_message)

        for i, url in enumerate(urls, 1):
            self.log_message(f"\n--- [{i}/{len(urls)}] İndiriliyor: {url} ---")
            downloader.download_playlist(url)

        self.log_message("\n=== Tüm İndirmeler Tamamlandı. Playlistler Oluşturuluyor... ===")
        self._regenerate_playlists()

        self.is_downloading = False
        self.after(0, lambda: self.btn_download.config(state=tk.NORMAL, text="🚀 İndirmeyi Başlat"))
        self.after(0, lambda: messagebox.showinfo("Tamamlandı", "Tüm parçalar ve çalma listeleri başarıyla arşivlendi."))

    def _regenerate_playlists(self) -> None:
        """
        Generates updated M3U8 playlist files for local tracks.
        """
        base_dir = Path(self.config.output_dir)
        if not base_dir.is_absolute():
            base_dir = Path(__file__).resolve().parent.parent / self.config.output_dir

        created = generate_all_playlists(output_dir=base_dir, storage_mode=self.config.storage_mode)
        self.log_message(f"[PLAYLIST] {len(created)} adet UTF-8 M3U8 çalma listesi güncellendi.")

    def _start_adb_push_thread(self) -> None:
        """
        Launches background thread to push local music files to Android.
        """
        if self.is_syncing:
            messagebox.showwarning("İşlem Devam Ediyor", "Aktarım zaten devam ediyor.")
            return

        base_dir = Path(self.config.output_dir)
        if not base_dir.is_absolute():
            base_dir = Path(__file__).resolve().parent.parent / self.config.output_dir

        if not base_dir.exists():
            messagebox.showwarning("Klasör Yok", f"İndirilenler klasörü bulunamadı: {base_dir}")
            return

        self.is_syncing = True
        self.btn_push.config(state=tk.DISABLED, text="⏳ Aktarılıyor...")
        threading.Thread(target=self._run_adb_push_task, args=(base_dir,), daemon=True).start()

    def _run_adb_push_task(self, local_dir: Path) -> None:
        """
        Executes ADB push and media scanner broadcast.
        """
        self.log_message("\n=== Android ADB Telefona Aktarım Başlatıldı ===")
        try:
            res = self.adb_engine.sync_library(
                local_music_dir=local_dir,
                remote_music_dir=self.config.adb_target
            )
            trans_mb = res.get("transferred_bytes", 0) / (1024 * 1024)
            self.log_message(f"=== Başarıyla Aktarıldı: {trans_mb:.2f} MB ===")
            self.after(0, lambda: messagebox.showinfo("Aktarım Başarılı", "Müzikler ve çalma listeleri telefona aktarıldı."))
        except Exception as e:
            self.log_message(f"[HATA] Aktarım başarısız: {e}")
            self.after(0, lambda err=e: messagebox.showerror("Aktarım Hatası", str(err)))
        finally:
            self.is_syncing = False
            self.after(0, lambda: self.btn_push.config(state=tk.NORMAL, text="📲 Telefona Aktar (ADB Push)"))


def launch_gui() -> None:
    """
    Instantiates and runs the SpotVault Tkinter main loop.
    """
    app = SpotVaultApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
