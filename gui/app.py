"""
Tkinter Desktop GUI for SpotVault v1.0.0.
Provides a modern dark-themed interface for configuring download quality,
managing M3U8 playlists, monitoring real-time console progress, and syncing to Android devices via ADB.
Includes complete Turkish (TR) and English (EN) internationalization with live switching.
"""

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
from core.i18n import get_text
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
    Main desktop window and UI controller for SpotVault v1.0.0.
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initializes window layout, state models, asynchronous workers, and visual widgets.
        """
        super().__init__()

        self.config_path = config_path or (Path(__file__).resolve().parent.parent / "spotvault_config.json")
        self.config = SpotVaultConfig.load(self.config_path)

        self.title(self.t("app_title"))
        self.geometry("1080x720")
        self.minsize(960, 640)
        self.configure(bg=BG_MAIN)

        self.adb_engine = AdbSyncEngine(log_callback=self.log_message)
        self.log_queue: queue.Queue = queue.Queue()
        self.is_downloading = False
        self.is_syncing = False
        self.active_downloader: Optional[SpotVaultDownloader] = None
        self.last_device_status: Dict[str, Any] = {}

        self._build_ui()
        self._load_saved_urls()
        self._start_log_consumer()
        self._start_device_monitor()

    def t(self, key: str, **kwargs: Any) -> str:
        """
        Translates key using active configured language.
        """
        return get_text(key, lang=self.config.language, **kwargs)

    def _build_ui(self) -> None:
        """
        Constructs header, left configuration sidebar, and right execution terminal.
        """
        header = tk.Frame(self, bg=BG_SURFACE, height=60, padx=20, pady=10)
        header.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header,
            text=self.t("app_header_title"),
            font=FONT_TITLE,
            fg=ACCENT_SPOTIFY,
            bg=BG_SURFACE
        )
        title_label.pack(side=tk.LEFT)

        self.lbl_subtitle = tk.Label(
            header,
            text=self.t("app_subtitle"),
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        self.lbl_subtitle.pack(side=tk.LEFT, padx=15, pady=4)

        # Language Switcher
        lang_frame = tk.Frame(header, bg=BG_SURFACE)
        lang_frame.pack(side=tk.RIGHT, padx=5)

        self.lbl_lang = tk.Label(
            lang_frame,
            text=self.t("lang_selector_label"),
            font=FONT_BODY,
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        self.lbl_lang.pack(side=tk.LEFT, padx=(0, 6))

        current_lang_display = "Türkçe (TR)" if self.config.language == "tr" else "English (EN)"
        self.lang_var = tk.StringVar(value=current_lang_display)
        self.lang_combobox = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["Türkçe (TR)", "English (EN)"],
            state="readonly",
            width=13
        )
        self.lang_combobox.pack(side=tk.LEFT)
        self.lang_combobox.bind("<<ComboboxSelected>>", self._on_language_changed)

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
        self.card_settings = tk.LabelFrame(
            parent,
            text=self.t("card_settings_title"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=FONT_SUBTITLE,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        self.card_settings.pack(fill=tk.X, pady=(0, 10))

        self.lbl_format = tk.Label(self.card_settings, text=self.t("lbl_format"), bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_HEADING)
        self.lbl_format.pack(anchor=tk.W, pady=(4, 2))

        self.format_var = tk.StringVar(value="MP3 (320 kbps)")
        fmt_dropdown = ttk.Combobox(
            self.card_settings,
            textvariable=self.format_var,
            values=["MP3 (320 kbps)", "MP3 (192 kbps)", "M4A (AAC auto)"],
            state="readonly"
        )
        fmt_dropdown.pack(fill=tk.X, pady=(0, 8))
        fmt_dropdown.bind("<<ComboboxSelected>>", self._on_format_changed)

        self.lbl_storage = tk.Label(self.card_settings, text=self.t("lbl_storage"), bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_HEADING)
        self.lbl_storage.pack(anchor=tk.W, pady=(4, 2))

        self.storage_var = tk.StringVar(value=self.config.storage_mode)
        self.rb_standalone = tk.Radiobutton(
            self.card_settings,
            text=self.t("radio_standalone"),
            variable=self.storage_var,
            value="standalone",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._on_storage_mode_changed
        )
        self.rb_standalone.pack(anchor=tk.W)

        self.rb_pool = tk.Radiobutton(
            self.card_settings,
            text=self.t("radio_pool"),
            variable=self.storage_var,
            value="pool_m3u8",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._on_storage_mode_changed
        )
        self.rb_pool.pack(anchor=tk.W, pady=(0, 8))

        self.artwork_var = tk.BooleanVar(value=self.config.embed_artwork)
        self.cb_art = tk.Checkbutton(
            self.card_settings,
            text=self.t("chk_artwork"),
            variable=self.artwork_var,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._save_config
        )
        self.cb_art.pack(anchor=tk.W)

        self.metadata_var = tk.BooleanVar(value=self.config.embed_metadata)
        self.cb_meta = tk.Checkbutton(
            self.card_settings,
            text=self.t("chk_metadata"),
            variable=self.metadata_var,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._save_config
        )
        self.cb_meta.pack(anchor=tk.W)

        self.lyrics_var = tk.BooleanVar(value=self.config.download_lyrics)
        self.cb_lyrics = tk.Checkbutton(
            self.card_settings,
            text=self.t("chk_lyrics"),
            variable=self.lyrics_var,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            selectcolor=BG_SURFACE,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._save_config
        )
        self.cb_lyrics.pack(anchor=tk.W)

    def _build_adb_card(self, parent: tk.Frame) -> None:
        """
        Creates Android device status badge, connection guide popup, and ADB Push action button.
        """
        self.card_adb = tk.LabelFrame(
            parent,
            text=self.t("card_adb_title"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=FONT_SUBTITLE,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        self.card_adb.pack(fill=tk.X)

        badge_row = tk.Frame(self.card_adb, bg=BG_CARD)
        badge_row.pack(fill=tk.X, pady=(4, 8))

        self.device_badge = tk.Label(
            badge_row,
            text=self.t("adb_disconnected"),
            bg="#334155",
            fg=TEXT_PRIMARY,
            font=FONT_HEADING,
            padx=8,
            pady=4
        )
        self.device_badge.pack(side=tk.LEFT)

        self.btn_refresh = tk.Button(
            badge_row,
            text=self.t("btn_adb_refresh"),
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            command=self._refresh_device_status
        )
        self.btn_refresh.pack(side=tk.RIGHT)

        self.btn_guide = tk.Button(
            self.card_adb,
            text=self.t("btn_adb_guide"),
            bg=BG_CARD,
            fg=ACCENT_PRIMARY,
            relief=tk.FLAT,
            anchor=tk.W,
            command=self._show_adb_guide
        )
        self.btn_guide.pack(fill=tk.X, pady=(0, 8))

        self.btn_push = tk.Button(
            self.card_adb,
            text=self.t("btn_adb_push"),
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

        self.lbl_urls = tk.Label(
            card,
            text=self.t("lbl_urls"),
            bg=BG_MAIN,
            fg=TEXT_PRIMARY,
            font=FONT_HEADING
        )
        self.lbl_urls.pack(anchor=tk.W, pady=(0, 4))

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
            text=self.t("btn_download"),
            bg=ACCENT_SPOTIFY,
            fg="#ffffff",
            font=FONT_HEADING,
            relief=tk.FLAT,
            padx=16,
            pady=8,
            command=self._start_download_thread
        )
        self.btn_download.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.btn_cancel = tk.Button(
            btn_bar,
            text=self.t("btn_cancel"),
            bg="#7f1d1d",
            fg="#fecaca",
            font=FONT_HEADING,
            relief=tk.FLAT,
            padx=14,
            pady=8,
            state=tk.DISABLED,
            command=self._on_cancel_clicked
        )
        self.btn_cancel.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_gen_m3u = tk.Button(
            btn_bar,
            text=self.t("btn_regenerate_m3u"),
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=12,
            pady=8,
            command=self._start_regenerate_playlists_thread
        )
        self.btn_gen_m3u.pack(side=tk.RIGHT)

    def _build_log_console(self, parent: tk.Frame) -> None:
        """
        Creates scrolling terminal text area for real-time operation output.
        """
        self.card_console = tk.LabelFrame(
            parent,
            text=f" {self.t('lbl_terminal')} ",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=FONT_SUBTITLE,
            padx=10,
            pady=8,
            relief=tk.FLAT,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        self.card_console.pack(fill=tk.BOTH, expand=True)

        self.console = tk.Text(
            self.card_console,
            bg="#030712",
            fg="#22c55e",
            font=FONT_CONSOLE,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=8,
            pady=8
        )
        scrollbar = tk.Scrollbar(self.card_console, command=self.console.yview)
        self.console.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _on_language_changed(self, event: Optional[Any] = None) -> None:
        """
        Handles language change event, updates configuration and refreshes all UI text dynamically.
        """
        val = self.lang_var.get()
        new_lang = "en" if "EN" in val else "tr"
        if new_lang != self.config.language:
            self.config.language = new_lang
            self._save_config()
            self._apply_translations()

    def _apply_translations(self) -> None:
        """
        Dynamically applies translations across all UI components.
        """
        self.title(self.t("app_title"))
        self.lbl_subtitle.config(text=self.t("app_subtitle"))
        self.lbl_lang.config(text=self.t("lang_selector_label"))

        # Settings
        self.card_settings.config(text=self.t("card_settings_title"))
        self.lbl_format.config(text=self.t("lbl_format"))
        self.lbl_storage.config(text=self.t("lbl_storage"))
        self.rb_standalone.config(text=self.t("radio_standalone"))
        self.rb_pool.config(text=self.t("radio_pool"))
        self.cb_art.config(text=self.t("chk_artwork"))
        self.cb_meta.config(text=self.t("chk_metadata"))
        self.cb_lyrics.config(text=self.t("chk_lyrics"))

        # ADB
        self.card_adb.config(text=self.t("card_adb_title"))
        self.btn_refresh.config(text=self.t("btn_adb_refresh"))
        self.btn_guide.config(text=self.t("btn_adb_guide"))
        if not self.is_syncing:
            self.btn_push.config(text=self.t("btn_adb_push"))

        # Download triggers
        self.lbl_urls.config(text=self.t("lbl_urls"))
        if not self.is_downloading:
            self.btn_download.config(text=self.t("btn_download"))
            self.btn_cancel.config(text=self.t("btn_cancel"))
        self.btn_gen_m3u.config(text=self.t("btn_regenerate_m3u"))

        # Console
        self.card_console.config(text=f" {self.t('lbl_terminal')} ")

        # Re-apply badge text with new language
        self._update_device_badge(self.last_device_status)

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
        self.last_device_status = status
        state = status.get("state", "none")
        serial = status.get("serial", "")

        if state == "device":
            self.device_badge.config(
                text=self.t("adb_connected", device=serial),
                bg="#064e3b",
                fg="#a7f3d0"
            )
            self.btn_push.config(state=tk.NORMAL)
        elif state == "unauthorized":
            unauth_msg = "🟡 Yetkisiz: Telefonda İzin Verin" if self.config.language == "tr" else "🟡 Unauthorized: Allow on phone"
            self.device_badge.config(
                text=unauth_msg,
                bg="#78350f",
                fg="#fde68a"
            )
            self.btn_push.config(state=tk.DISABLED)
        else:
            self.device_badge.config(
                text=self.t("adb_disconnected"),
                bg="#334155",
                fg=TEXT_SECONDARY
            )
            self.btn_push.config(state=tk.DISABLED)

    def _refresh_device_status(self) -> None:
        """
        Manually triggers an immediate device poll.
        """
        scan_msg = "⚪ Taranıyor..." if self.config.language == "tr" else "⚪ Scanning..."
        self.device_badge.config(text=scan_msg, bg="#334155", fg=TEXT_SECONDARY)
        threading.Thread(target=self._query_device_state_async, daemon=True).start()

    def _show_adb_guide(self) -> None:
        """
        Displays modal instructions on enabling USB debugging and trusting PC.
        """
        messagebox.showinfo(self.t("guide_window_title"), self.t("guide_content"))

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

    def _on_cancel_clicked(self) -> None:
        """
        Signals cancellation to the active downloader engine.
        """
        if self.active_downloader:
            self.active_downloader.cancel()
            self.btn_cancel.config(state=tk.DISABLED, text=self.t("btn_cancel_active"))

    def _start_download_thread(self) -> None:
        """
        Validates input and launches background downloader execution.
        """
        if self.is_downloading:
            messagebox.showwarning(self.t("title_warning"), self.t("msg_already_downloading"))
            return

        urls_raw = self.url_text.get("1.0", tk.END).strip()
        urls = [line.strip() for line in urls_raw.splitlines() if line.strip() and not line.startswith("#")]

        if not urls:
            messagebox.showwarning(self.t("title_warning"), self.t("msg_no_urls"))
            return

        self.is_downloading = True
        self.btn_download.config(state=tk.DISABLED, text=self.t("btn_download_active"))
        self.btn_cancel.config(state=tk.NORMAL, text=self.t("btn_cancel"))
        threading.Thread(target=self._run_download_task, args=(urls,), daemon=True).start()

    def _run_download_task(self, urls: List[str]) -> None:
        """
        Executes download and fallback matcher pipeline across provided URLs with try/finally safety.
        """
        self.log_message(self.t("log_start_download", count=len(urls)))
        try:
            self.active_downloader = SpotVaultDownloader(self.config, log_callback=self.log_message)

            for i, url in enumerate(urls, 1):
                if self.active_downloader.cancel_requested:
                    self.log_message(f"\n{self.t('log_download_cancelled')}")
                    break
                self.log_message(f"\n{self.t('log_download_item', index=i, total=len(urls), url=url)}")
                self.active_downloader.download_playlist(url)

            if not self.active_downloader.cancel_requested:
                self.log_message(f"\n{self.t('log_playlists_updating')}")
                self._regenerate_playlists(pool_mapping=self.active_downloader.pool_playlist_mapping)
                self.after(0, lambda: messagebox.showinfo(self.t("title_success"), self.t("msg_download_complete")))
        except Exception as e:
            self.log_message(f"\n[HATA] {e}")
            self.after(0, lambda err=e: messagebox.showerror(self.t("title_error"), self.t("msg_download_error", error=str(err))))
        finally:
            self.is_downloading = False
            self.active_downloader = None
            self.after(0, lambda: self.btn_download.config(state=tk.NORMAL, text=self.t("btn_download")))
            self.after(0, lambda: self.btn_cancel.config(state=tk.DISABLED, text=self.t("btn_cancel")))

    def _regenerate_playlists(self, pool_mapping: Optional[Dict[str, List[str]]] = None) -> List[Path]:
        """
        Generates updated M3U8 playlist files for local tracks.
        """
        base_dir = Path(self.config.output_dir)
        if not base_dir.is_absolute():
            base_dir = Path(__file__).resolve().parent.parent / self.config.output_dir

        created = generate_all_playlists(
            output_dir=base_dir,
            storage_mode=self.config.storage_mode,
            pool_playlist_mapping=pool_mapping
        )
        if created:
            self.log_message(self.t("log_playlists_updated", count=len(created)))
        else:
            self.log_message(self.t("log_no_playlists_created"))
        return created

    def _start_regenerate_playlists_thread(self) -> None:
        """
        Launches an asynchronous worker thread to regenerate M3U8 playlists without freezing the GUI.
        """
        self.btn_gen_m3u.config(state=tk.DISABLED, text=self.t("btn_regenerate_m3u_active"))
        threading.Thread(target=self._run_regenerate_playlists_task, daemon=True).start()

    def _run_regenerate_playlists_task(self) -> None:
        """
        Worker execution for background M3U8 playlist generation.
        """
        try:
            created = self._regenerate_playlists()
            if not created:
                self.after(0, lambda: messagebox.showinfo(self.t("title_info"), self.t("msg_no_playlists_found")))
            else:
                self.after(0, lambda c=len(created): messagebox.showinfo(self.t("title_success"), self.t("msg_playlists_regenerated", count=c)))
        except Exception as e:
            self.log_message(f"[HATA] Playlist yenileme başarısız: {e}")
            self.after(0, lambda err=e: messagebox.showerror(self.t("title_error"), self.t("msg_playlists_error", error=str(err))))
        finally:
            self.after(0, lambda: self.btn_gen_m3u.config(state=tk.NORMAL, text=self.t("btn_regenerate_m3u")))

    def _start_adb_push_thread(self) -> None:
        """
        Launches background thread to push local music files to Android.
        """
        if self.is_syncing:
            messagebox.showwarning(self.t("title_warning"), self.t("msg_sync_in_progress"))
            return

        base_dir = Path(self.config.output_dir)
        if not base_dir.is_absolute():
            base_dir = Path(__file__).resolve().parent.parent / self.config.output_dir

        if not base_dir.exists():
            messagebox.showwarning(self.t("title_warning"), self.t("msg_downloads_dir_missing", path=str(base_dir)))
            return

        self.is_syncing = True
        self.btn_push.config(state=tk.DISABLED, text=self.t("btn_adb_push_active"))
        threading.Thread(target=self._run_adb_push_task, args=(base_dir,), daemon=True).start()

    def _run_adb_push_task(self, local_dir: Path) -> None:
        """
        Executes ADB push and media scanner broadcast.
        """
        self.log_message(f"\n{self.t('log_adb_push_start')}")
        try:
            res = self.adb_engine.sync_library(
                local_music_dir=local_dir,
                remote_music_dir=self.config.adb_target
            )
            trans_mb = res.get("transferred_bytes", 0) / (1024 * 1024)
            self.log_message(f"=== {trans_mb:.2f} MB ===\n{self.t('log_adb_push_complete')}")
            self.after(0, lambda: messagebox.showinfo(self.t("title_success"), self.t("msg_sync_success")))
        except Exception as e:
            self.log_message(self.t("log_adb_push_error", error=str(e)))
            self.after(0, lambda err=e: messagebox.showerror(self.t("title_error"), self.t("msg_sync_error", error=str(err))))
        finally:
            self.is_syncing = False
            self.after(0, lambda: self.btn_push.config(state=tk.NORMAL, text=self.t("btn_adb_push")))


def launch_gui() -> None:
    """
    Instantiates and runs the SpotVault Tkinter main loop.
    """
    app = SpotVaultApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
