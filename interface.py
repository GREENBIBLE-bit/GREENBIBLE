import re
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from tkinter import ttk, simpledialog, messagebox
from songs import open_songs
import sqlite3
import tempfile
import threading
import wave
import os
import json
from pathlib import Path
from tkinter import ttk, colorchooser
from announcements import AnnouncementWindow
import sounddevice as sd
import speech_recognition as sr
import time
from deepgram import DeepgramClient
from deepgram.core.events import EventType

from smart_parser import extract_reference as smart_extract_reference
from smart_parser import BOOKS as SMART_BOOKS
import ndi_renderer
from presentation import GreenBiblePresentation
from license_window import show_license_window


KJV_DATABASE = "kjv.sqlite"


BOOKS = {
    "Genesis": 1,
    "Exodus": 2,
    "Leviticus": 3,
    "Numbers": 4,
    "Deuteronomy": 5,
    "Joshua": 6,
    "Judges": 7,
    "Ruth": 8,
    "1 Samuel": 9,
    "2 Samuel": 10,
    "1 Kings": 11,
    "2 Kings": 12,
    "1 Chronicles": 13,
    "2 Chronicles": 14,
    "Ezra": 15,
    "Nehemiah": 16,
    "Esther": 17,
    "Job": 18,
    "Psalms": 19,
    "Proverbs": 20,
    "Ecclesiastes": 21,
    "Song of Solomon": 22,
    "Isaiah": 23,
    "Jeremiah": 24,
    "Lamentations": 25,
    "Ezekiel": 26,
    "Daniel": 27,
    "Hosea": 28,
    "Joel": 29,
    "Amos": 30,
    "Obadiah": 31,
    "Jonah": 32,
    "Micah": 33,
    "Nahum": 34,
    "Habakkuk": 35,
    "Zephaniah": 36,
    "Haggai": 37,
    "Zechariah": 38,
    "Malachi": 39,
    "Matthew": 40,
    "Mark": 41,
    "Luke": 42,
    "John": 43,
    "Acts": 44,
    "Romans": 45,
    "1 Corinthians": 46,
    "2 Corinthians": 47,
    "Galatians": 48,
    "Ephesians": 49,
    "Philippians": 50,
    "Colossians": 51,
    "1 Thessalonians": 52,
    "2 Thessalonians": 53,
    "1 Timothy": 54,
    "2 Timothy": 55,
    "Titus": 56,
    "Philemon": 57,
    "Hebrews": 58,
    "James": 59,
    "1 Peter": 60,
    "2 Peter": 61,
    "1 John": 62,
    "2 John": 63,
    "3 John": 64,
    "Jude": 65,
    "Revelation": 66,
}


class GreenBibleInterface:
    def __init__(self, root):
        self.root = root

        self.root.title("GREENBIBLE - LIVE")
        self.root.geometry("1250x780")
        self.root.configure(bg="#111111")

        self.settings_file = "greenbible_settings.json"

        self.settings = {
            "microphone": "Default Microphone",
            "listen_time": "6 seconds",
            "bible_version": "KJV",
            "ndi_name": "GREENBIBLE",
            "resolution": "1280x720",
            "deepgram_api_key": "",
        }

        try:
            settings_path = Path(self.settings_file)

            if settings_path.exists():
                saved_settings = json.loads(
                    settings_path.read_text(
                        encoding="utf-8"
                    )
                )

                if isinstance(saved_settings, dict):
                    self.settings.update(saved_settings)

        except Exception as e:
            print(
                "GREENBIBLE SETTINGS LOAD ERROR:",
                e
            )

        self.themes = {
            "Classic Dark": {
                "background": "#111111",
                "text": "white",
                "accent": "yellow",
                "button": "#222222"
            },
            "Church Gold": {
                "background": "#15120A",
                "text": "#FFF4CC",
                "accent": "#FFD700",
                "button": "#332B10"
            },
            "Blue Night": {
                "background": "#071525",
                "text": "#EAF4FF",
                "accent": "#66CCFF",
                "button": "#102A43"
            },
            "White Light": {
                "background": "#F4F4F4",
                "text": "#111111",
                "accent": "#B8860B",
                "button": "#DDDDDD"
            },
            "Custom": {
                "background": "#111111",
                "text": "white",
                "accent": "yellow",
                "button": "#222222"
            }
        }

        self.current_theme = "Classic Dark"

        # Voice engine state
        self.voice_running = False
        self.voice_thread = None
        self.stop_event = threading.Event()
        self.current_book = None
        self.current_chapter = None
        self.current_verse = None
        self.presentation = None

        # Media state
        self.media_window = None
        self.media_player = None
        self.media_instance = None
        self.media_image = None
        self.media_path = None

        # Start the existing native NDI renderer.
        try:
            self.ndi = ndi_renderer.start()
            print("GREENBIBLE NDI: ACTIVE")
        except Exception as e:
            print(f"GREENBIBLE NDI ERROR: {e}")
            self.ndi = None

            self.ndi = None
            print("GREENBIBLE NDI ERROR:", e)

        self.build_interface()

    def build_interface(self):
        bg = "#0b0f0d"
        panel = "#121815"
        panel2 = "#171d19"
        border = "#263229"
        accent = "#00e676"
        gold = "#d7b56d"
        white = "#f5f7f6"
        muted = "#8f9b94"
        danger = "#b3261e"

        self.root.title("GREENBIBLE")
        self.root.geometry("1400x850")
        self.root.minsize(1180, 700)
        self.root.configure(bg=bg)

        # ============================================================
        # HEADER
        # ============================================================
        header = tk.Frame(
            self.root,
            bg=panel,
            height=78
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=panel)
        brand.pack(
            side="left",
            fill="y",
            padx=18
        )

        # GREENBIBLE LOGO
        try:
            from PIL import Image, ImageTk

            logo_path = Path("logo.png")

            if logo_path.exists():
                logo_image = Image.open(logo_path)
                logo_image.thumbnail((58, 58), Image.LANCZOS)

                self.logo_photo = ImageTk.PhotoImage(logo_image)

                tk.Label(
                    brand,
                    image=self.logo_photo,
                    bg=panel
                ).pack(
                    side="left",
                    padx=(0, 12),
                    pady=8
                )
        except Exception as e:
            print("GREENBIBLE LOGO ERROR:", e)

        tk.Label(
            brand,
            text="GREENBIBLE",
            bg=panel,
            fg=white,
            font=("Arial", 24, "bold")
        ).pack(
            side="left",
            pady=18
        )

        tk.Label(
            brand,
            text="  LIVE BIBLE CONTROL",
            bg=panel,
            fg=accent,
            font=("Arial", 10, "bold")
        ).pack(
            side="left",
            pady=21
        )

        header_status = tk.Frame(
            header,
            bg=panel
        )
        header_status.pack(
            side="right",
            padx=20
        )

        self.header_voice = tk.Label(
            header_status,
            text="VOICE READY",
            bg=panel2,
            fg=muted,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8
        )
        self.header_voice.pack(side="left", padx=5)

        tk.Label(
            header_status,
            text="DEEPGRAM",
            bg=panel2,
            fg=accent,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8
        ).pack(side="left", padx=5)

        tk.Label(
            header_status,
            text="NDI LIVE",
            bg=panel2,
            fg=accent,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8
        ).pack(side="left", padx=5)

        tk.Label(
            header_status,
            text="KJV",
            bg=panel2,
            fg=gold,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8
        ).pack(side="left", padx=5)

        # ============================================================
        # MAIN AREA
        # ============================================================
        workspace = tk.Frame(
            self.root,
            bg=bg
        )
        workspace.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14
        )

        # ============================================================
        # LEFT CONTROL PANEL
        # ============================================================
        left = tk.Frame(
            workspace,
            bg=panel,
            width=245,
            highlightbackground=border,
            highlightthickness=1
        )
        left.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )
        left.pack_propagate(False)

        # Allow the complete control panel to remain visible.
        left.bind("<Configure>", lambda event: left.update_idletasks())

        tk.Label(
            left,
            text="CONTROL",
            bg=panel,
            fg=muted,
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(22, 10)
        )

        def control_button(text, command, active="#1d2a22"):
            return tk.Button(
                left,
                text=text,
                command=command,
                bg=panel,
                fg=white,
                activebackground=active,
                activeforeground=accent,
                relief="flat",
                bd=0,
                anchor="w",
                font=("Arial", 10, "bold"),
                padx=16,
                pady=8,
                cursor="hand2"
            )

        voice_btn = control_button(
            "VOICE BIBLE",
            self.start_listening
        )
        voice_btn.pack(fill="x")

        tk.Button(
            left,
            text="STOP LISTENING",
            command=self.stop_listening,
            bg=danger,
            fg=white,
            activebackground="#d13a31",
            activeforeground=white,
            relief="flat",
            bd=0,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=13,
            cursor="hand2"
        ).pack(
            fill="x",
            padx=15,
            pady=(4, 10)
        )

        search_btn = control_button(
            "BIBLE SEARCH",
            self.manual_bible_search
        )
        search_btn.pack(fill="x")

        presentation_btn = control_button(
            "LIVE PRESENTATION",
            self.open_live_presentation
        )
        presentation_btn.pack(fill="x")

        tk.Frame(
            left,
            bg=border,
            height=1
        ).pack(
            fill="x",
            padx=16,
            pady=12
        )

        tk.Label(
            left,
            text="MEDIA",
            bg=panel,
            fg=muted,
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(2, 8)
        )

        media_btn = control_button(
            "MEDIA DISPLAY",
            self.open_media
        )
        media_btn.pack(fill="x")

        songs_btn = control_button(
            "SONGS",
            lambda: open_songs(self)
        )
        songs_btn.pack(fill="x")

        announcements_btn = control_button(
            "ANNOUNCEMENTS",
            self.open_announcements
        )
        announcements_btn.pack(fill="x")

        tk.Frame(
            left,
            bg=border,
            height=1
        ).pack(
            fill="x",
            padx=16,
            pady=12
        )

        tk.Label(
            left,
            text="SYSTEM",
            bg=panel,
            fg=muted,
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(2, 8)
        )

        settings_btn = control_button(
            "SETTINGS",
            self.open_settings
        )
        settings_btn.pack(fill="x")

        license_btn = control_button(
            "LICENSE / ACTIVATION",
            lambda: show_license_window(self.root)
        )
        license_btn.pack(fill="x")

        themes_btn = control_button(
            "THEMES",
            self.open_themes
        )
        themes_btn.pack(fill="x")

        # ============================================================
        # CENTER SCRIPTURE AREA
        # ============================================================
        center = tk.Frame(
            workspace,
            bg=bg
        )
        center.pack(
            side="left",
            fill="both",
            expand=True
        )

        title_row = tk.Frame(
            center,
            bg=bg
        )
        title_row.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            title_row,
            text="ON-AIR SCRIPTURE",
            bg=bg,
            fg=muted,
            font=("Arial", 11, "bold")
        ).pack(side="left")

        self.status = tk.Label(
            title_row,
            text="READY",
            bg=panel2,
            fg=accent,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=7
        )
        self.status.pack(side="right")

        reference_card = tk.Frame(
            center,
            bg=panel,
            highlightbackground=border,
            highlightthickness=1
        )
        reference_card.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            reference_card,
            text="CURRENT REFERENCE",
            bg=panel,
            fg=muted,
            font=("Arial", 9, "bold")
        ).pack(
            anchor="w",
            padx=22,
            pady=(15, 2)
        )

        self.reference = tk.Label(
            reference_card,
            text="No Scripture selected",
            bg=panel,
            fg=gold,
            font=("Arial", 27, "bold"),
            anchor="w"
        )
        self.reference.pack(
            fill="x",
            padx=22,
            pady=(0, 16)
        )

        # SPOKEN WORDS BAR
        # ============================================================
        heard_bar = tk.Frame(
            center,
            bg="#090c0a",
            height=76,
            highlightbackground=accent,
            highlightthickness=1
        )
        heard_bar.pack(
            fill="x",
            side="bottom",
            padx=0,
            pady=(10, 0)
        )
        heard_bar.pack_propagate(False)

        tk.Label(
            heard_bar,
            text="SPOKEN WORDS",
            bg="#090c0a",
            fg=accent,
            font=("Arial", 11, "bold"),
            width=18,
            anchor="w"
        ).pack(
            side="left",
            padx=(18, 8)
        )

        self.heard_text = tk.Label(
            heard_bar,
            text="Waiting for speech...",
            bg="#090c0a",
            fg=white,
            font=("Arial", 14),
            anchor="w",
            justify="left"
        )
        self.heard_text.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8
        )

        tk.Label(
            heard_bar,
            text="Deepgram",
            bg="#090c0a",
            fg=muted,
            font=("Arial", 9, "bold")
        ).pack(
            side="right",
            padx=18
        )

        self.scripture_card = tk.Frame(
            center,
            bg="#080b09",
            highlightbackground=border,
            highlightthickness=1
        )
        self.scripture_card.pack(
            fill="both",
            expand=True
        )

        self.scripture_kjv = tk.Label(
            self.scripture_card,
            text="KJV",
            bg="#080b09",
            fg=accent,
            font=("Arial", 10, "bold")
        )
        self.scripture_kjv.pack(
            anchor="w",
            padx=24,
            pady=(18, 0)
        )

        self.scripture_text = tk.Text(
            self.scripture_card,
            bg="#080b09",
            fg=white,
            insertbackground=white,
            font=("Georgia", 25),
            wrap="word",
            relief="flat",
            bd=0,
            padx=28,
            pady=24,
            spacing1=4,
            spacing3=8
        )
        self.scripture_text.pack(
            fill="both",
            expand=True
        )

        self.scripture_text.insert(
            "1.0",
            "Waiting for Scripture..."
        )
        self.scripture_text.config(
            state="disabled"
        )

        # ============================================================
        # RIGHT LIVE PREVIEW
        # ============================================================
        right = tk.Frame(
            workspace,
            bg=panel,
            width=380,
            highlightbackground=border,
            highlightthickness=1
        )
        right.pack(
            side="right",
            fill="y",
            padx=(12, 0)
        )
        right.pack_propagate(False)

        tk.Label(
            right,
            text="NDI OUTPUT",
            bg=panel,
            fg=muted,
            font=("Arial", 10, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 8)
        )

        preview = tk.Frame(
            right,
            bg="#000000",
            highlightbackground="#2d3a30",
            highlightthickness=1
        )
        preview.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 16)
        )

        tk.Label(
            preview,
            text="LIVE PREVIEW",
            bg="#000000",
            fg=accent,
            font=("Arial", 10, "bold")
        ).pack(
            pady=(18, 10)
        )

        self.preview_reference = tk.Label(
            preview,
            text="No Scripture selected",
            bg="#000000",
            fg=white,
            font=("Arial", 25, "bold"),
            wraplength=310,
            justify="center"
        )
        self.preview_reference.pack(
            padx=20,
            pady=(10, 4)
        )

        self.preview_version = tk.Label(
            preview,
            text="KJV",
            bg="#000000",
            fg=gold,
            font=("Arial", 12, "bold")
        )
        self.preview_version.pack(
            pady=(0, 16)
        )

        self.preview_verse = tk.Label(
            preview,
            text="Waiting for Scripture...",
            bg="#000000",
            fg=white,
            font=("Georgia", 17),
            wraplength=305,
            justify="center"
        )
        self.preview_verse.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=18
        )

        tk.Label(
            right,
            text="NDI SOURCE: GREENBIBLE",
            bg=panel,
            fg=accent,
            font=("Arial", 9, "bold")
        ).pack(
            pady=(0, 18)
        )

        # ============================================================
    # ============================================================
    # MEDIA DISPLAY
    # ============================================================
    def open_media(self):
        """Open the GREENBIBLE Media Display window."""
        try:
            if self.media_window is not None:
                try:
                    if self.media_window.winfo_exists():
                        self.media_window.deiconify()
                        self.media_window.lift()
                        return
                except Exception:
                    pass

            self.media_window = tk.Toplevel(self.root)
            self.media_window.title("GREENBIBLE - MEDIA DISPLAY")
            self.media_window.geometry("1100x700")
            self.media_window.minsize(800, 550)
            self.media_window.configure(bg="#050505")

            # Header
            header = tk.Frame(
                self.media_window,
                bg="#111111",
                height=58
            )
            header.pack(fill="x")
            header.pack_propagate(False)

            tk.Label(
                header,
                text="GREENBIBLE MEDIA",
                bg="#111111",
                fg="#00e676",
                font=("Arial", 16, "bold")
            ).pack(side="left", padx=20)

            self.media_status = tk.Label(
                header,
                text="READY",
                bg="#111111",
                fg="#8f9b94",
                font=("Arial", 10, "bold")
            )
            self.media_status.pack(side="right", padx=20)

            # Main display area
            self.media_display = tk.Frame(
                self.media_window,
                bg="#000000"
            )
            self.media_display.pack(
                fill="both",
                expand=True,
                padx=12,
                pady=12
            )

            self.media_message = tk.Label(
                self.media_display,
                text="MEDIA DISPLAY\n\nOpen an image or video",
                bg="#000000",
                fg="#8f9b94",
                font=("Arial", 20, "bold"),
                justify="center"
            )
            self.media_message.place(
                relx=0.5,
                rely=0.5,
                anchor="center"
            )

            # Controls
            controls = tk.Frame(
                self.media_window,
                bg="#111111",
                height=72
            )
            controls.pack(fill="x")
            controls.pack_propagate(False)

            button_options = {
                "bg": "#1b241f",
                "fg": "#f5f7f6",
                "activebackground": "#26352d",
                "activeforeground": "#00e676",
                "relief": "flat",
                "bd": 0,
                "font": ("Arial", 10, "bold"),
                "padx": 18,
                "pady": 10,
                "cursor": "hand2"
            }

            tk.Button(
                controls,
                text="OPEN IMAGE",
                command=self.media_open_image,
                **button_options
            ).pack(side="left", padx=(16, 6), pady=14)

            tk.Button(
                controls,
                text="OPEN VIDEO",
                command=self.media_open_video,
                **button_options
            ).pack(side="left", padx=6, pady=14)

            tk.Button(
                controls,
                text="PLAY",
                command=self.media_play,
                **button_options
            ).pack(side="left", padx=6, pady=14)

            tk.Button(
                controls,
                text="PAUSE",
                command=self.media_pause,
                **button_options
            ).pack(side="left", padx=6, pady=14)

            tk.Button(
                controls,
                text="BACK 10 SEC",
                command=self.media_back,
                **button_options
            ).pack(side="left", padx=6, pady=14)

            tk.Button(
                controls,
                text="FORWARD 10 SEC",
                command=self.media_forward,
                **button_options
            ).pack(side="left", padx=6, pady=14)

            tk.Button(
                controls,
                text="STOP",
                command=self.media_stop,
                **button_options
            ).pack(side="left", padx=6, pady=14)

            tk.Button(
                controls,
                text="CLEAR",
                command=self.media_clear,
                bg="#6b1f1f",
                fg="#ffffff",
                activebackground="#8b2929",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                font=("Arial", 10, "bold"),
                padx=18,
                pady=10,
                cursor="hand2"
            ).pack(side="right", padx=16, pady=14)

            self.media_window.protocol(
                "WM_DELETE_WINDOW",
                self.close_media
            )

        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE MEDIA",
                f"Could not open Media Display:\n\n{e}"
            )

    def _media_set_status(self, text):
        if hasattr(self, "media_status"):
            try:
                self.media_status.config(text=text)
            except Exception:
                pass

    def media_open_image(self):
        try:
            from tkinter import filedialog
            from PIL import Image, ImageTk

            path = filedialog.askopenfilename(
                title="GREENBIBLE - Open Image",
                filetypes=[
                    ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("All Files", "*.*")
                ]
            )

            if not path:
                return

            self.media_stop()

            image = Image.open(path)
            image.thumbnail((1000, 580), Image.LANCZOS)

            self.media_image = ImageTk.PhotoImage(image)

            self.media_message.place_forget()

            for widget in self.media_display.winfo_children():
                widget.destroy()

            label = tk.Label(
                self.media_display,
                image=self.media_image,
                bg="#000000"
            )
            label.pack(
                fill="both",
                expand=True
            )

            self.media_path = path
            self._media_set_status(
                "IMAGE: " + Path(path).name
            )

            # Send the selected image to the existing GREENBIBLE NDI output
            try:
                if self.ndi:
                    self.ndi.update_image(path)
                    print("MEDIA NDI: IMAGE SENT ->", path)
            except Exception as ndi_error:
                print("MEDIA NDI ERROR:", ndi_error)

        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE MEDIA",
                f"Could not open image:\n\n{e}"
            )

    def _find_vlc(self):
        import os
        import vlc

        vlc_path = r"C:\Program Files\VideoLAN\VLC"

        if os.path.exists(os.path.join(vlc_path, "libvlc.dll")):
            os.add_dll_directory(vlc_path)

        self.media_instance = vlc.Instance(
            "--no-video-title-show"
        )

        return self.media_instance

    def media_open_video(self):
        try:
            from tkinter import filedialog

            path = filedialog.askopenfilename(
                title="GREENBIBLE - Open Video",
                filetypes=[
                    ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv *.webm"),
                    ("MP4", "*.mp4"),
                    ("All Files", "*.*")
                ]
            )

            if not path:
                return

            self.media_stop()

            instance = self._find_vlc()

            self.media_player = instance.media_player_new()

            media = instance.media_new(path)
            self.media_player.set_media(media)

            self.media_message.place_forget()

            for widget in self.media_display.winfo_children():
                widget.destroy()

            video_panel = tk.Frame(
                self.media_display,
                bg="#000000"
            )
            video_panel.pack(
                fill="both",
                expand=True
            )

            self.media_video_panel = video_panel

            self.media_window.update_idletasks()

            self.media_player.set_hwnd(
                video_panel.winfo_id()
            )

            self.media_path = path

            # Send the moving video to GREENBIBLE NDI
            try:
                if self.ndi:
                    self.ndi.update_video(path)
                    print("MEDIA NDI: MOVING VIDEO SENT ->", path)
            except Exception as ndi_error:
                print("MEDIA VIDEO NDI ERROR:", ndi_error)

            self.media_player.play()

            self._media_set_status(
                "VIDEO: " + Path(path).name
            )

        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE MEDIA",
                f"Could not open video:\n\n{e}"
            )

    def media_forward(self):
        try:
            if self.media_player:
                current = self.media_player.get_time()
                self.media_player.set_time(current + 10000)

            if self.ndi:
                self.ndi.seek_video(10)

        except Exception as e:
            print("MEDIA FORWARD ERROR:", e)

    def media_back(self):
        try:
            if self.media_player:
                current = self.media_player.get_time()
                self.media_player.set_time(max(0, current - 10000))

            if self.ndi:
                self.ndi.seek_video(-10)

        except Exception as e:
            print("MEDIA BACK ERROR:", e)

    def media_play(self):
        try:
            if self.media_player:
                self.media_player.play()

            if self.ndi and getattr(self, "media_path", None):
                if str(self.media_path).lower().endswith(
                    (".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm")
                ):
                    self.ndi.resume_video()

            self._media_set_status("PLAYING")
        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE MEDIA",
                str(e)
            )

    def media_pause(self):
        try:
            if self.media_player:
                self.media_player.pause()

            if self.ndi and getattr(self, "media_path", None):
                if str(self.media_path).lower().endswith(
                    (".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm")
                ):
                    self.ndi.pause_video()

            self._media_set_status("PAUSED")
        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE MEDIA",
                str(e)
            )

    def media_stop(self):
        try:
            if self.media_player:
                self.media_player.stop()

            if self.ndi:
                self.ndi.stop_video()

        except Exception:
            pass

    def media_clear(self):
        try:
            self.media_stop()

            self.media_player = None
            self.media_image = None
            self.media_path = None

            if hasattr(self, "media_display"):
                for widget in self.media_display.winfo_children():
                    widget.destroy()

                self.media_message = tk.Label(
                    self.media_display,
                    text="MEDIA DISPLAY\n\nOpen an image or video",
                    bg="#000000",
                    fg="#8f9b94",
                    font=("Arial", 20, "bold"),
                    justify="center"
                )
                self.media_message.place(
                    relx=0.5,
                    rely=0.5,
                    anchor="center"
                )

            self._media_set_status("READY")

        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE MEDIA",
                str(e)
            )

    def close_media(self):
        try:
            self.media_stop()
        except Exception:
            pass

        try:
            if self.media_window:
                self.media_window.destroy()
        except Exception:
            pass

        self.media_window = None
        self.media_player = None
        self.media_image = None
        self.media_path = None

    def _update_center_scripture(self, text):
        if hasattr(self, "scripture_text"):
            self.scripture_text.config(state="normal")
            self.scripture_text.delete("1.0", tk.END)
            self.scripture_text.insert("1.0", text)
            self.scripture_text.config(state="disabled")

    def open_announcements(self):
        try:
            AnnouncementWindow(self)
        except Exception as e:
            print("GREENBIBLE ANNOUNCEMENTS ERROR:", e)

    def _listen_seconds(self):
        try:
            return int(self.settings["listen_time"].split()[0])
        except Exception:
            return 6

    def start_listening(self):
        if self.voice_running:
            self.status.config(text="ALREADY LISTENING")
            return

        self.voice_running = True
        self.stop_event.clear()
        self.status.config(text="LISTENING...")
        self.voice_thread = threading.Thread(
            target=self.listen_loop,
            daemon=True
        )
        self.voice_thread.start()

    def stop_listening(self):
        self.stop_event.set()
        self.voice_running = False
        self.root.after(0, lambda: self.status.config(text="STOPPED"))
        print("GREENBIBLE: Listening stopped.")

    def listen_loop(self):
        key = (
            self.settings.get("deepgram_api_key", "").strip()
            or os.getenv("DEEPGRAM_API_KEY")
        )

        if not key:
            print("GREENBIBLE: DEEPGRAM KEY NOT FOUND")
            self.root.after(
                0,
                lambda: self.status.config(text="DEEPGRAM KEY NOT FOUND")
            )
            return

        client = DeepgramClient(api_key=key)
        print("GREENBIBLE: DEEPGRAM STARTING...")

        try:
            with client.listen.v1.connect(
                model="nova-3",
                language="en-US",
                smart_format=True,
                punctuate=True,
                encoding="linear16",
                channels=1,
                sample_rate=48000,
                interim_results=True,
                vad_events=True,
                endpointing=200,
            ) as connection:

                final_parts = []

                def opened(_):
                    print("GREENBIBLE: DEEPGRAM CONNECTED")
                    self.root.after(
                        0,
                        lambda: self.status.config(text="DEEPGRAM LISTENING")
                    )

                def message(msg):
                    try:
                        text = msg.channel.alternatives[0].transcript
                    except Exception:
                        return

                    if not text:
                        return

                    self.root.after(
                        0,
                        lambda heard=text: self.heard_text.config(text=heard)
                    )

                    is_final = getattr(msg, "is_final", False)
                    speech_final = getattr(msg, "speech_final", False)

                    if is_final:
                        final_parts.append(text.strip())

                    if speech_final:
                        utterance = " ".join(final_parts).strip()
                        final_parts.clear()

                        if not utterance:
                            utterance = text.strip()

                        print("GREENBIBLE FINAL:", utterance)

                        command = utterance.lower().strip()
                        command = re.sub(
                            r"[^a-z0-9\s:]",
                            " ",
                            command
                        )
                        command = re.sub(
                            r"\s+",
                            " ",
                            command
                        ).strip()

                        # Common Deepgram substitutions.
                        command = command.replace(
                            "versus", "verse"
                        )
                        command = command.replace(
                            "vest", "verse"
                        )
                        command = command.replace(
                            "base", "verse"
                        )

                        # ------------------------------------------------
                        # NEXT VERSE
                        # ------------------------------------------------
                        next_commands = (
                            "next",
                            "next verse",
                            "next verses",
                            "go next",
                            "go to next verse",
                            "go to next verses",
                            "go to the next verse",
                        )

                        if command in next_commands:
                            print(
                                "GREENBIBLE command: NEXT VERSE"
                            )
                            self.root.after(
                                0,
                                self.next_verse
                            )
                            return

                        # ------------------------------------------------
                        # PREVIOUS VERSE
                        # ------------------------------------------------
                        previous_commands = (
                            "previous",
                            "previous verse",
                            "previous verses",
                            "last verse",
                            "go back",
                            "go to previous verse",
                            "go to previous verses",
                            "go to the previous verse",
                        )

                        if command in previous_commands:
                            print(
                                "GREENBIBLE command: PREVIOUS VERSE"
                            )
                            self.root.after(
                                0,
                                self.previous_verse
                            )
                            return

                        # ------------------------------------------------
                        # GO TO VERSE N
                        # Uses current book/chapter.
                        # ------------------------------------------------
                        number_words = {
                            "zero": 0,
                            "one": 1,
                            "two": 2,
                            "three": 3,
                            "four": 4,
                            "five": 5,
                            "six": 6,
                            "seven": 7,
                            "eight": 8,
                            "nine": 9,
                            "ten": 10,
                            "eleven": 11,
                            "twelve": 12,
                            "thirteen": 13,
                            "fourteen": 14,
                            "fifteen": 15,
                            "sixteen": 16,
                            "seventeen": 17,
                            "eighteen": 18,
                            "nineteen": 19,
                            "twenty": 20,
                            "thirty": 30,
                            "forty": 40,
                            "fifty": 50,
                            "sixty": 60,
                            "seventy": 70,
                            "eighty": 80,
                            "ninety": 90,
                        }

                        go_verse = re.match(
                            r"^(?:go to|jump to|open)"
                            r"(?: the)?"
                            r" verse (.+)$",
                            command,
                            re.IGNORECASE
                        )

                        if go_verse:
                            words = go_verse.group(1).strip()
                            target_verse = None

                            if words.isdigit():
                                target_verse = int(words)
                            elif words in number_words:
                                target_verse = number_words[words]

                            if (
                                target_verse is not None
                                and self.current_book
                                and self.current_chapter
                            ):
                                print(
                                    "GREENBIBLE command: GO TO",
                                    f"{self.current_book} "
                                    f"{self.current_chapter}:"
                                    f"{target_verse}"
                                )

                                self.root.after(
                                    0,
                                    self.load_scripture,
                                    self.current_book,
                                    self.current_chapter,
                                    target_verse
                                )
                                return

                        # ------------------------------------------------
                        # GO TO / OPEN / JUMP TO A FULL REFERENCE
                        # ------------------------------------------------
                        go_to_text = re.sub(
                            r"^(?:go to|jump to|open)"
                            r"(?: the)?\\s+",
                            "",
                            command,
                            count=1,
                            flags=re.IGNORECASE
                        ).strip()

                        reference = self.extract_spoken_reference(
                            go_to_text
                        )

                        if (
                            not reference
                            and self.looks_like_bible_reference(
                                utterance
                            )
                        ):
                            result = smart_extract_reference(
                                utterance
                            )

                            if result:
                                if isinstance(result, (tuple, list)):
                                    if len(result) >= 3:
                                        reference = (
                                            f"{result[0]} "
                                            f"{result[1]}:{result[2]}"
                                        )
                                    elif len(result) == 1:
                                        reference = str(result[0])
                                else:
                                    reference = str(result)

                        if reference:
                            parsed = self.parse_reference_text(
                                reference
                            )

                            if parsed:
                                book, chapter, verse = parsed
                                print(
                                    "GREENBIBLE REFERENCE:",
                                    f"{book} {chapter}:{verse}"
                                )
                                self.root.after(
                                    0,
                                    self.load_scripture,
                                    book,
                                    chapter,
                                    verse
                                )

                def error(err):
                    print("GREENBIBLE DEEPGRAM ERROR:", err)

                connection.on(EventType.OPEN, opened)
                connection.on(EventType.MESSAGE, message)
                connection.on(EventType.ERROR, error)

                threading.Thread(
                    target=connection.start_listening,
                    daemon=True
                ).start()

                def microphone_callback(
                    data, frames, time_info, status
                ):
                    try:
                        connection.send_media(bytes(data))
                    except Exception as e:
                        print("GREENBIBLE AUDIO ERROR:", e)

                with sd.RawInputStream(
                    samplerate=48000,
                    blocksize=4800,
                    channels=1,
                    dtype="int16",
                    device=1,
                    callback=microphone_callback,
                ):
                    while not self.stop_event.is_set():
                        time.sleep(0.05)

                try:
                    connection.send_finalize()
                except Exception:
                    pass

        except Exception as e:
            print("GREENBIBLE DEEPGRAM CONNECTION ERROR:", e)

        finally:
            self.voice_running = False
            print("GREENBIBLE: Deepgram listening stopped.")

    def looks_like_bible_reference(self, text):
        text = str(text).lower().strip()
        text = re.sub(r"[,\.\?!;:]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return False

        words = text.split()

        # Explicit Bible-reference language is a strong signal.
        if "chapter" in words or "verse" in words:
            return True

        # A colon-like reference was present before punctuation
        # was normalized.
        if ":" in str(text):
            return True

        # Compact references such as:
        # John 3 16
        # John three sixteen
        # Psalm one one nine two
        for start in range(len(words)):
            for end in range(start + 1, min(start + 4, len(words)) + 1):
                book_text = " ".join(words[start:end])

                if self.parse_reference_text(
                    f"{book_text} 1:1"
                ):
                    remaining = words[end:]

                    if len(remaining) >= 2:
                        numeric = 0

                        number_words = {
                            "zero", "one", "two", "three",
                            "four", "five", "six", "seven",
                            "eight", "nine", "ten", "eleven",
                            "twelve", "thirteen", "fourteen",
                            "fifteen", "sixteen", "seventeen",
                            "eighteen", "nineteen", "twenty",
                            "thirty", "forty", "fifty", "sixty",
                            "seventy", "eighty", "ninety",
                            "hundred"
                        }

                        for word in remaining:
                            if word.isdigit() or word in number_words:
                                numeric += 1
                            else:
                                break

                        if numeric >= 2:
                            return True

        return False


    def extract_spoken_reference(self, utterance):
        text = str(utterance).lower().strip()
        text = re.sub(r"[,\.\?!;:]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Common speech-recognition substitutions.
        replacements = {
            "maxes": "mark",
            "max": "mark",
            "mac": "mark",
            "mack": "mark",
            "marc": "mark",

            "look": "luke",
            "looke": "luke",
            "luk": "luke",

            "versus": "verse",
            "vest": "verse",
            "best": "verse",
            "base": "verse",

            "chap": "chapter",
            "chapt": "chapter",
        }

        words = text.split()
        words = [replacements.get(w, w) for w in words]
        text = " ".join(words)

        if not text:
            return None

        ones = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "eleven": 11,
            "twelve": 12,
            "thirteen": 13,
            "fourteen": 14,
            "fifteen": 15,
            "sixteen": 16,
            "seventeen": 17,
            "eighteen": 18,
            "nineteen": 19,
        }

        tens = {
            "twenty": 20,
            "thirty": 30,
            "forty": 40,
            "fifty": 50,
            "sixty": 60,
            "seventy": 70,
            "eighty": 80,
            "ninety": 90,
        }

        digit_words = {
            "zero", "one", "two", "three", "four",
            "five", "six", "seven", "eight", "nine"
        }

        def is_num_word(word):
            return (
                word.isdigit()
                or word in ones
                or word in tens
                or word == "hundred"
                or word == "and"
            )

        def words_to_number(words):
            if not words:
                return None

            # "one one nine" -> 119
            # "one zero seven" -> 107
            if all(
                w in digit_words
                or (w.isdigit() and len(w) == 1)
                for w in words
            ):
                return int(
                    "".join(
                        str(
                            {"zero": 0, "one": 1, "two": 2,
                             "three": 3, "four": 4, "five": 5,
                             "six": 6, "seven": 7, "eight": 8,
                             "nine": 9}[w]
                        )
                        if w in digit_words
                        else w
                        for w in words
                    )
                )

            if len(words) == 1 and words[0].isdigit():
                return int(words[0])

            total = 0
            current = 0

            for word in words:
                if word.isdigit():
                    current += int(word)
                elif word in ones:
                    current += ones[word]
                elif word in tens:
                    current += tens[word]
                elif word == "hundred":
                    if current == 0:
                        current = 1
                    current *= 100
                elif word == "and":
                    continue
                else:
                    return None

            return total + current

        tokens = text.split()

        # ------------------------------------------------------------
        # 1. Normal numeric reference.
        # ------------------------------------------------------------
        direct = self.parse_reference_text(text)
        if direct:
            return f"{direct[0]} {direct[1]}:{direct[2]}"

        # ------------------------------------------------------------
        # 2. "John chapter three verse sixteen"
        #    Also handles filler before the book:
        #    "So John chapter three verse sixteen"
        # ------------------------------------------------------------
        for start in range(len(tokens)):
            for chapter_pos in range(start + 1, len(tokens)):
                if tokens[chapter_pos] != "chapter":
                    continue

                book_text = " ".join(
                    tokens[start:chapter_pos]
                ).strip()

                if not book_text:
                    continue

                if not self.parse_reference_text(
                    f"{book_text} 1:1"
                ):
                    continue

                verse_pos = None
                for x in range(chapter_pos + 1, len(tokens)):
                    if tokens[x] == "verse":
                        verse_pos = x
                        break

                if verse_pos is None:
                    continue

                chapter_words = tokens[
                    chapter_pos + 1:verse_pos
                ]

                chapter_words = [
                    w for w in chapter_words
                    if w != "and"
                ]

                chapter = words_to_number(
                    chapter_words
                )

                if chapter is None:
                    continue

                verse_words = []

                for w in tokens[verse_pos + 1:]:
                    if not is_num_word(w):
                        break
                    verse_words.append(w)

                verse = words_to_number(
                    verse_words
                )

                if verse is None:
                    continue

                candidate = (
                    f"{book_text} "
                    f"{chapter}:{verse}"
                )

                if self.parse_reference_text(candidate):
                    return candidate

        # ------------------------------------------------------------
        # 3. "Psalm 23 verse one"
        #    "Psalm one one nine verse two"
        #    "Proverb four verse one"
        # ------------------------------------------------------------
        for start in range(len(tokens)):
            for verse_pos in range(start + 2, len(tokens)):
                if tokens[verse_pos] != "verse":
                    continue

                for book_end in range(
                    start + 1,
                    verse_pos
                ):
                    book_text = " ".join(
                        tokens[start:book_end]
                    ).strip()

                    if not self.parse_reference_text(
                        f"{book_text} 1:1"
                    ):
                        continue

                    chapter_words = tokens[
                        book_end:verse_pos
                    ]

                    if not chapter_words:
                        continue

                    if not all(
                        is_num_word(w)
                        for w in chapter_words
                    ):
                        continue

                    chapter = words_to_number(
                        chapter_words
                    )

                    verse_words = []

                    for w in tokens[verse_pos + 1:]:
                        if not is_num_word(w):
                            break
                        verse_words.append(w)

                    verse = words_to_number(
                        verse_words
                    )

                    if chapter is None or verse is None:
                        continue

                    candidate = (
                        f"{book_text} "
                        f"{chapter}:{verse}"
                    )

                    if self.parse_reference_text(candidate):
                        return candidate

        # ------------------------------------------------------------
        # 4. Compact speech:
        #    "John three six" -> John 3:6
        #    "John three sixteen" -> John 3:16
        #    "Psalm one one nine two" -> Psalm 119:2
        # ------------------------------------------------------------
        for start in range(len(tokens)):
            for book_end in range(
                start + 1,
                len(tokens)
            ):
                book_text = " ".join(
                    tokens[start:book_end]
                ).strip()

                if not self.parse_reference_text(
                    f"{book_text} 1:1"
                ):
                    continue

                remaining = tokens[book_end:]

                number_words = []

                for w in remaining:
                    if not is_num_word(w):
                        break
                    number_words.append(w)

                if len(number_words) < 2:
                    continue

                chapter_words = number_words[:-1]
                verse_words = number_words[-1:]

                chapter = words_to_number(
                    chapter_words
                )

                verse = words_to_number(
                    verse_words
                )

                if chapter is None or verse is None:
                    continue

                candidate = (
                    f"{book_text} "
                    f"{chapter}:{verse}"
                )

                if self.parse_reference_text(candidate):
                    return candidate

        return None


    def parse_reference_text(self, reference):
        text = str(reference).strip()
        text = re.sub(r"\s+", " ", text)
        text = text.replace(",", " ")

        match = re.match(
            r"^(.+?)\s+(\d+)\s*:\s*(\d+)$",
            text,
            re.IGNORECASE
        )

        if not match:
            match = re.match(
                r"^(.+?)\s+chapter\s+(\d+)\s+verse\s+(\d+)$",
                text,
                re.IGNORECASE
            )

        if not match:
            match = re.match(
                r"^(.+?)\s+(\d+)\s+verse\s+(\d+)$",
                text,
                re.IGNORECASE
            )

        if not match:
            match = re.match(
                r"^(.+?)\s+(\d+)\s+(\d+)$",
                text,
                re.IGNORECASE
            )

        if not match:
            return None

        spoken_book = match.group(1).strip()
        chapter = int(match.group(2))
        verse = int(match.group(3))

        aliases = {
            "gen": "Genesis",
            "ge": "Genesis",

            "ex": "Exodus",
            "exo": "Exodus",

            "lev": "Leviticus",
            "le": "Leviticus",

            "num": "Numbers",
            "nu": "Numbers",

            "deut": "Deuteronomy",
            "deu": "Deuteronomy",

            "jos": "Joshua",
            "josh": "Joshua",

            "judg": "Judges",
            "jdg": "Judges",

            "ruth": "Ruth",

            "1sam": "1 Samuel",
            "1 sam": "1 Samuel",
            "1st sam": "1 Samuel",
            "first samuel": "1 Samuel",

            "2sam": "2 Samuel",
            "2 sam": "2 Samuel",
            "2nd sam": "2 Samuel",
            "second samuel": "2 Samuel",

            "1kgs": "1 Kings",
            "1kgs": "1 Kings",
            "1 kings": "1 Kings",
            "first kings": "1 Kings",

            "2kgs": "2 Kings",
            "2 kings": "2 Kings",
            "second kings": "2 Kings",

            "1chr": "1 Chronicles",
            "1 chr": "1 Chronicles",
            "1 chronicles": "1 Chronicles",
            "first chronicles": "1 Chronicles",

            "2chr": "2 Chronicles",
            "2 chr": "2 Chronicles",
            "2 chronicles": "2 Chronicles",
            "second chronicles": "2 Chronicles",

            "ezra": "Ezra",
            "neh": "Nehemiah",
            "est": "Esther",

            "job": "Job",

            "ps": "Psalms",
            "psalm": "Psalms",
            "psalms": "Psalms",

            "prov": "Proverbs",
            "pro": "Proverbs",
        "proverb": "Proverbs",

            "eccl": "Ecclesiastes",
            "ecc": "Ecclesiastes",

            "song": "Song of Solomon",
            "songs": "Song of Solomon",
            "sos": "Song of Solomon",
            "song of songs": "Song of Solomon",
            "song of solomon": "Song of Solomon",
        "psalms of solomon": "Song of Solomon",

            "isa": "Isaiah",
            "jer": "Jeremiah",
            "lam": "Lamentations",
            "ezek": "Ezekiel",
            "dan": "Daniel",

            "hos": "Hosea",
            "joe": "Joel",
            "joel": "Joel",
            "amos": "Amos",
            "obad": "Obadiah",
            "obadiah": "Obadiah",
            "jon": "Jonah",
            "jonah": "Jonah",
            "mic": "Micah",
            "nah": "Nahum",
            "hab": "Habakkuk",
            "zeph": "Zephaniah",
            "hag": "Haggai",
            "zech": "Zechariah",
            "mal": "Malachi",

            "matt": "Matthew",
            "mat": "Matthew",
            "mt": "Matthew",

            "mark": "Mark",
        "max": "Mark",
        "maxes": "Mark",
        "mac": "Mark",
        "mack": "Mark",
        "marc": "Mark",
            "mk": "Mark",
            "mrk": "Mark",

            "luke": "Luke",
        "look": "Luke",
        "looke": "Luke",
        "luk": "Luke",
            "lk": "Luke",

            "john": "John",
            "jn": "John",
            "jh": "John",

            "acts": "Acts",
            "act": "Acts",

            "rom": "Romans",
            "ro": "Romans",

            "1cor": "1 Corinthians",
            "1 cor": "1 Corinthians",
            "1corinthians": "1 Corinthians",
            "1 corinthians": "1 Corinthians",
            "first corinthians": "1 Corinthians",

            "2cor": "2 Corinthians",
            "2 cor": "2 Corinthians",
            "2corinthians": "2 Corinthians",
            "2 corinthians": "2 Corinthians",
            "second corinthians": "2 Corinthians",

            "gal": "Galatians",
            "eph": "Ephesians",
            "phil": "Philippians",
            "php": "Philippians",
            "col": "Colossians",

            "1thess": "1 Thessalonians",
            "1 thess": "1 Thessalonians",
            "1 thessalonians": "1 Thessalonians",
            "first thessalonians": "1 Thessalonians",

            "2thess": "2 Thessalonians",
            "2 thess": "2 Thessalonians",
            "2 thessalonians": "2 Thessalonians",
            "second thessalonians": "2 Thessalonians",

            "1tim": "1 Timothy",
            "1 tim": "1 Timothy",
            "1 timothy": "1 Timothy",
            "first timothy": "1 Timothy",

            "2tim": "2 Timothy",
            "2 tim": "2 Timothy",
            "2 timothy": "2 Timothy",
            "second timothy": "2 Timothy",

            "titus": "Titus",
            "tit": "Titus",

            "philem": "Philemon",
            "phm": "Philemon",

            "heb": "Hebrews",
            "hebrews": "Hebrews",

            "jas": "James",
            "jam": "James",
            "james": "James",

            "1pet": "1 Peter",
            "1 pet": "1 Peter",
            "1 peter": "1 Peter",
            "first peter": "1 Peter",

            "2pet": "2 Peter",
            "2 pet": "2 Peter",
            "2 peter": "2 Peter",
            "second peter": "2 Peter",

            "1jn": "1 John",
            "1 jn": "1 John",
            "1 john": "1 John",
            "first john": "1 John",

            "2jn": "2 John",
            "2 jn": "2 John",
            "2 john": "2 John",
            "second john": "2 John",

            "3jn": "3 John",
            "3 jn": "3 John",
            "3 john": "3 John",
            "third john": "3 John",

            "jude": "Jude",
            "rev": "Revelation",
            "revelations": "Revelation"
        }

        book_lower = re.sub(
            r"\s+", " ", spoken_book
        ).strip().lower()

        book = aliases.get(book_lower)

        if book is None:
            for canonical in BOOKS:
                if canonical.lower() == book_lower:
                    book = canonical
                    break

        if book not in BOOKS:
            return None

        return book, chapter, verse

    def show_announcement(self, title, text):
        self.reference.config(text="")
        self.status.config(text="ANNOUNCEMENT LOADED")

        if hasattr(self, "scripture_text"):
            self.scripture_text.config(state="normal")
            self.scripture_text.delete("1.0", tk.END)
            self.scripture_text.insert("1.0", text)
            self.scripture_text.config(state="disabled")

        self.preview_reference.config(text="")
        self.preview_version.config(text="")
        self.preview_verse.config(text=text)

        if self.ndi:
            try:
                self.ndi.update("", text)
            except Exception as e:
                print("GREENBIBLE NDI ANNOUNCEMENT UPDATE ERROR:", e)

        if self.presentation and self.presentation.window.winfo_exists():
            try:
                self.presentation.show_verse("", text)
            except Exception as e:
                print("GREENBIBLE PRESENTATION ANNOUNCEMENT ERROR:", e)

    def show_song(self, title, lyrics):
        self.reference.config(text="")
        self.status.config(text="SONG LOADED")

        if hasattr(self, "scripture_text"):
            self.scripture_text.config(state="normal")
            self.scripture_text.delete("1.0", tk.END)
            self.scripture_text.insert("1.0", lyrics)
            self.scripture_text.config(state="disabled")

        self.preview_reference.config(text="")
        self.preview_version.config(text="")
        self.preview_verse.config(text=lyrics)

        if self.ndi:
            try:
                self.ndi.update("", lyrics)
            except Exception as e:
                print("GREENBIBLE NDI SONG UPDATE ERROR:", e)

        if self.presentation and self.presentation.window.winfo_exists():
            try:
                self.presentation.show_verse("", lyrics)
            except Exception as e:
                print("GREENBIBLE PRESENTATION SONG ERROR:", e)

    def load_scripture(self, book, chapter, verse):
        if book not in BOOKS:
            self.status.config(text="BOOK NOT FOUND")
            return

        book_id = BOOKS[book]

        with sqlite3.connect(KJV_DATABASE) as connection:
            row = connection.execute(
                """
                SELECT text
                FROM verses
                WHERE book_id=? AND chapter=? AND number=?
                """,
                (book_id, chapter, verse)
            ).fetchone()

        if not row:
            self.status.config(text="VERSE NOT FOUND")
            return

        self.current_book = book
        self.current_chapter = chapter
        self.current_verse = verse

        self.show_scripture(book, chapter, verse, row[0])

    def apply_scripture_display_style(self):
        """Apply saved Scripture style to the Scripture display only."""
        try:
            bg = self.settings.get("scripture_bg", "#080b09")
            text_color = self.settings.get("scripture_text", "#FFFFFF")
            size = int(self.settings.get("scripture_font_size", 25))
            bold = bool(self.settings.get("scripture_bold", False))
            align = self.settings.get("scripture_align", "center")

            ref_color = self.settings.get("reference_color", "#FFD700")
            ref_size = int(self.settings.get("reference_font_size", 27))
            ref_bold = bool(self.settings.get("reference_bold", True))
            ref_position = self.settings.get(
                "reference_position",
                "top left"
            )

            if not hasattr(self, "scripture_text"):
                return

            # Scripture area only
            self.scripture_card.configure(bg=bg)

            self.scripture_kjv.configure(
                bg=bg,
                fg=ref_color
            )

            self.scripture_text.configure(
                bg=bg,
                fg=text_color,
                insertbackground=text_color,
                font=(
                    "Georgia",
                    size,
                    "bold" if bold else "normal"
                ),
                justify=align
            )

            # Reference card
            self.reference.configure(
                fg=ref_color,
                font=(
                    "Arial",
                    ref_size,
                    "bold" if ref_bold else "normal"
                )
            )

            if ref_position == "top center":
                self.reference.configure(anchor="center")
            elif ref_position == "top right":
                self.reference.configure(anchor="e")
            else:
                self.reference.configure(anchor="w")

        except Exception as e:
            print("SCRIPTURE DISPLAY STYLE ERROR:", e)

    def show_scripture(self, book, chapter, verse, text):
        reference = f"{book} {chapter}:{verse}"

        self.reference.config(text=reference)
        self.status.config(text="SCRIPTURE LOADED")
        self.preview_reference.config(text=reference)
        self.preview_version.config(text="KJV")
        self.preview_verse.config(text=text)

        if hasattr(self, "scripture_text"):
            # Apply Scripture style only when Scripture is displayed.
            self.apply_scripture_display_style()

            self.scripture_text.config(state="normal")
            self.scripture_text.delete("1.0", tk.END)
            self.scripture_text.insert("1.0", text)
            self.scripture_text.config(state="disabled")

        if self.ndi:
            try:
                self.ndi.update(reference, text)
            except Exception as e:
                print("GREENBIBLE NDI UPDATE ERROR:", e)

        if self.presentation and self.presentation.window.winfo_exists():
            self.presentation.show_verse(reference, text)

    def next_verse(self):
        self.navigate_verse("next")

    def previous_verse(self):
        self.navigate_verse("previous")

    def navigate_verse(self, direction):
        if not self.current_book:
            print("GREENBIBLE: No current Scripture.")
            return

        book_id = BOOKS[self.current_book]

        with sqlite3.connect(KJV_DATABASE) as connection:
            if direction == "next":
                row = connection.execute(
                    """
                    SELECT chapter, number, text
                    FROM verses
                    WHERE book_id=?
                      AND (
                          chapter > ?
                          OR (chapter = ? AND number > ?)
                      )
                    ORDER BY chapter, number
                    LIMIT 1
                    """,
                    (
                        book_id,
                        self.current_chapter,
                        self.current_chapter,
                        self.current_verse
                    )
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT chapter, number, text
                    FROM verses
                    WHERE book_id=?
                      AND (
                          chapter < ?
                          OR (chapter = ? AND number < ?)
                      )
                    ORDER BY chapter DESC, number DESC
                    LIMIT 1
                    """,
                    (
                        book_id,
                        self.current_chapter,
                        self.current_chapter,
                        self.current_verse
                    )
                ).fetchone()

        if not row:
            print("GREENBIBLE: No more verses in this direction.")
            return

        chapter, verse, text = row

        print(
            f"GREENBIBLE navigation: "
            f"{self.current_book} {chapter}:{verse}"
        )

        self.show_scripture(
            self.current_book,
            chapter,
            verse,
            text
        )

    def open_live_presentation(self):
        if self.presentation:
            try:
                if self.presentation.window.winfo_exists():
                    self.presentation.window.lift()
                    return
            except Exception:
                pass

        self.presentation = GreenBiblePresentation(
            self.root,
            on_close=self._presentation_closed
        )

        if self.current_book:
            reference = (
                f"{self.current_book} "
                f"{self.current_chapter}:{self.current_verse}"
            )

            with sqlite3.connect(KJV_DATABASE) as connection:
                row = connection.execute(
                    """
                    SELECT text
                    FROM verses
                    WHERE book_id=? AND chapter=? AND number=?
                    """,
                    (
                        BOOKS[self.current_book],
                        self.current_chapter,
                        self.current_verse
                    )
                ).fetchone()

            if row:
                self.presentation.show_verse(
                    reference,
                    row[0]
                )

    def _presentation_closed(self):
        self.presentation = None
    def manual_bible_search(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("GREENBIBLE - BIBLE SEARCH")
        search_window.geometry("650x300")
        search_window.minsize(600, 260)
        search_window.configure(bg="#151515")
        search_window.transient(self.root)
        search_window.grab_set()

        tk.Label(
            search_window,
            text="BIBLE SEARCH",
            bg="#151515",
            fg="#00ff66",
            font=("Arial", 24, "bold")
        ).pack(pady=(20, 10))

        tk.Label(
            search_window,
            text="Enter Bible reference",
            bg="#151515",
            fg="white",
            font=("Arial", 15, "bold")
        ).pack(pady=(5, 8))

        reference_var = tk.StringVar()

        entry = tk.Entry(
            search_window,
            textvariable=reference_var,
            bg="#252525",
            fg="white",
            insertbackground="white",
            font=("Arial", 20),
            justify="center"
        )
        entry.pack(
            fill="x",
            padx=45,
            ipady=10
        )

        tk.Label(
            search_window,
            text="Example: John 3:16   |   Psalm 23:1   |   Genesis 1:1",
            bg="#151515",
            fg="#bbbbbb",
            font=("Arial", 11)
        ).pack(pady=8)

        def do_search():
            reference = reference_var.get().strip()

            if not reference:
                messagebox.showwarning(
                    "Bible Search",
                    "Please enter a Bible reference.",
                    parent=search_window
                )
                return

            parsed = self.parse_reference_text(reference)

            if not parsed:
                messagebox.showerror(
                    "Bible Search",
                    "Reference not recognized.\n\n"
                    "Examples:\n"
                    "John 3:16\n"
                    "Genesis 1:1\n"
                    "Psalm 23:1\n"
                    "1 Corinthians 13:4",
                    parent=search_window
                )
                return

            book, chapter, verse = parsed

            print(
                f"GREENBIBLE MANUAL SEARCH: "
                f"{book} {chapter}:{verse}"
            )

            try:
                self.load_scripture(
                    book,
                    chapter,
                    verse
                )

                search_window.destroy()

            except Exception as e:
                print(
                    "GREENBIBLE MANUAL SEARCH ERROR:",
                    e
                )

                messagebox.showerror(
                    "Bible Search Error",
                    str(e),
                    parent=search_window
                )

        tk.Button(
            search_window,
            text="SEARCH",
            command=do_search,
            bg="#008844",
            fg="white",
            activebackground="#00aa55",
            activeforeground="white",
            font=("Arial", 16, "bold"),
            width=16,
            height=2
        ).pack(pady=15)

        entry.focus_set()

        search_window.bind(
            "<Return>",
            lambda event: do_search()
        )

    def test_scripture(self):
        book = "John"
        chapter = 3
        verse = 16

        book_id = BOOKS[book]

        with sqlite3.connect(KJV_DATABASE) as connection:
            row = connection.execute(
                """
                SELECT text
                FROM verses
                WHERE book_id=? AND chapter=? AND number=?
                """,
                (book_id, chapter, verse)
            ).fetchone()

        if not row:
            self.status.config(text="VERSE NOT FOUND")
            return

        text = row[0]
        self.current_book = book
        self.current_chapter = chapter
        self.current_verse = verse
        self.show_scripture(book, chapter, verse, text)

    def open_settings(self):
        window = tk.Toplevel(self.root)
        window.title("GREENBIBLE - SETTINGS")
        window.geometry("700x1000")
        window.minsize(650, 850)
        window.configure(bg="#151515")

        tk.Label(
            window,
            text="GREENBIBLE SETTINGS",
            bg="#151515",
            fg="white",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        # Scrollable settings area
        settings_canvas = tk.Canvas(
            window,
            bg="#151515",
            highlightthickness=0
        )

        settings_scrollbar = tk.Scrollbar(
            window,
            orient="vertical",
            command=settings_canvas.yview
        )

        settings_canvas.configure(
            yscrollcommand=settings_scrollbar.set
        )

        settings_scrollbar.pack(
            side="right",
            fill="y"
        )

        settings_canvas.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(40, 0)
        )

        frame = tk.Frame(
            settings_canvas,
            bg="#151515"
        )

        settings_canvas.create_window(
            (0, 0),
            window=frame,
            anchor="nw"
        )

        def update_settings_scrollregion(event=None):
            settings_canvas.configure(
                scrollregion=settings_canvas.bbox("all")
            )

        frame.bind(
            "<Configure>",
            update_settings_scrollregion
        )

        settings_canvas.bind_all(
            "<MouseWheel>",
            lambda event: settings_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )
        )

        tk.Label(
            frame,
            text="Microphone",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        microphone = ttk.Combobox(
            frame,
            values=[
                "Default Microphone",
                "Microphone Array",
                "External USB Microphone"
            ],
            state="readonly"
        )
        microphone.set(self.settings["microphone"])
        microphone.pack(fill="x", pady=(5, 15))

        tk.Label(
            frame,
            text="Listening Duration",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        listen_time = ttk.Combobox(
            frame,
            values=[
                "3 seconds",
                "5 seconds",
                "6 seconds",
                "8 seconds",
                "10 seconds"
            ],
            state="readonly"
        )
        listen_time.set(self.settings["listen_time"])
        listen_time.pack(fill="x", pady=(5, 15))

        tk.Label(
            frame,
            text="Bible Version",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        bible_version = ttk.Combobox(
            frame,
            values=["KJV"],
            state="readonly"
        )
        bible_version.set(self.settings["bible_version"])
        bible_version.pack(fill="x", pady=(5, 15))

        tk.Label(
            frame,
            text="NDI Source Name",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        ndi_name = tk.Entry(frame)
        ndi_name.insert(0, self.settings["ndi_name"])
        ndi_name.pack(fill="x", pady=(5, 15))

        tk.Label(
            frame,
            text="Resolution",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        resolution = ttk.Combobox(
            frame,
            values=["1280x720", "1920x1080"],
            state="readonly"
        )
        resolution.set(self.settings["resolution"])
        resolution.pack(fill="x", pady=(5, 15))

        tk.Label(
            frame,
            text="Deepgram API Key",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        deepgram_key = tk.Entry(
            frame,
            show="*"
        )
        deepgram_key.insert(
            0,
            self.settings.get(
                "deepgram_api_key",
                ""
            )
        )
        deepgram_key.pack(
            fill="x",
            pady=(5, 15)
        )

        tk.Label(
            frame,
            text="The key is saved locally on this PC.",
            bg="#151515",
            fg="#aaaaaa",
            font=("Arial", 9)
        ).pack(anchor="w", pady=(0, 10))

        def save_settings():
            self.settings["microphone"] = microphone.get()
            self.settings["listen_time"] = listen_time.get()
            self.settings["bible_version"] = bible_version.get()
            self.settings["ndi_name"] = ndi_name.get()
            self.settings["resolution"] = resolution.get()
            self.settings["deepgram_api_key"] = (
                deepgram_key.get().strip()
            )

            try:
                Path(self.settings_file).write_text(
                    json.dumps(
                        self.settings,
                        indent=2
                    ),
                    encoding="utf-8"
                )
                print(
                    "GREENBIBLE SETTINGS SAVED"
                )
            except Exception as e:
                print(
                    "GREENBIBLE SETTINGS SAVE ERROR:",
                    e
                )

            window.destroy()

        # ------------------------------------------------------------
        # SCRIPTURE PRESENTATION SETTINGS
        # ------------------------------------------------------------

        tk.Label(
            frame,
            text="SCRIPTURE PRESENTATION",
            bg="#151515",
            fg="#00ff66",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(15, 10))

        scripture_frame = tk.Frame(
            frame,
            bg="#151515"
        )
        scripture_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        # Background
        tk.Label(
            scripture_frame,
            text="Scripture Background",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        bg_row = tk.Frame(
            scripture_frame,
            bg="#151515"
        )
        bg_row.pack(fill="x", pady=(5, 10))

        scripture_bg = tk.Entry(bg_row)
        scripture_bg.insert(
            0,
            self.settings.get(
                "scripture_bg",
                "#000000"
            )
        )
        scripture_bg.pack(
            side="left",
            fill="x",
            expand=True
        )

        def choose_scripture_bg():
            from tkinter import colorchooser

            color = colorchooser.askcolor(
                title="Choose Scripture Background Color",
                initialcolor=scripture_bg.get()
            )

            if color and color[1]:
                scripture_bg.delete(0, tk.END)
                scripture_bg.insert(0, color[1])

        tk.Button(
            bg_row,
            text="COLOR",
            command=choose_scripture_bg,
            bg="#333333",
            fg="white",
            relief="flat"
        ).pack(
            side="left",
            padx=(8, 0)
        )

        # Text color
        tk.Label(
            scripture_frame,
            text="Verse Text Color",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        text_row = tk.Frame(
            scripture_frame,
            bg="#151515"
        )
        text_row.pack(fill="x", pady=(5, 10))

        scripture_text = tk.Entry(text_row)
        scripture_text.insert(
            0,
            self.settings.get(
                "scripture_text",
                "#FFFFFF"
            )
        )
        scripture_text.pack(
            side="left",
            fill="x",
            expand=True
        )

        def choose_scripture_text():
            from tkinter import colorchooser

            color = colorchooser.askcolor(
                title="Choose Verse Text Color",
                initialcolor=scripture_text.get()
            )

            if color and color[1]:
                scripture_text.delete(0, tk.END)
                scripture_text.insert(0, color[1])

        tk.Button(
            text_row,
            text="COLOR",
            command=choose_scripture_text,
            bg="#333333",
            fg="white",
            relief="flat"
        ).pack(
            side="left",
            padx=(8, 0)
        )

        # Verse font size
        tk.Label(
            scripture_frame,
            text="Verse Font Size",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        scripture_size = ttk.Combobox(
            scripture_frame,
            values=[
                "28",
                "32",
                "36",
                "38",
                "42",
                "46",
                "50",
                "56",
                "64"
            ],
            state="readonly"
        )
        scripture_size.set(
            str(
                self.settings.get(
                    "scripture_font_size",
                    38
                )
            )
        )
        scripture_size.pack(
            fill="x",
            pady=(5, 10)
        )

        # Bold
        scripture_bold_var = tk.BooleanVar(
            value=self.settings.get(
                "scripture_bold",
                False
            )
        )

        tk.Checkbutton(
            scripture_frame,
            text="Bold Scripture Text",
            variable=scripture_bold_var,
            bg="#151515",
            fg="white",
            selectcolor="#333333",
            activebackground="#151515",
            activeforeground="white"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        # Verse alignment
        tk.Label(
            scripture_frame,
            text="Verse Text Alignment",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        scripture_align = ttk.Combobox(
            scripture_frame,
            values=[
                "left",
                "center",
                "right"
            ],
            state="readonly"
        )
        scripture_align.set(
            self.settings.get(
                "scripture_align",
                "center"
            )
        )
        scripture_align.pack(
            fill="x",
            pady=(5, 10)
        )

        # Reference position
        tk.Label(
            scripture_frame,
            text="Verse Reference Position",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        reference_position = ttk.Combobox(
            scripture_frame,
            values=[
                "top left",
                "top center",
                "top right"
            ],
            state="readonly"
        )
        reference_position.set(
            self.settings.get(
                "reference_position",
                "top left"
            )
        )
        reference_position.pack(
            fill="x",
            pady=(5, 10)
        )

        # Reference color
        tk.Label(
            scripture_frame,
            text="Verse Reference Color",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        reference_row = tk.Frame(
            scripture_frame,
            bg="#151515"
        )
        reference_row.pack(
            fill="x",
            pady=(5, 10)
        )

        reference_color = tk.Entry(reference_row)
        reference_color.insert(
            0,
            self.settings.get(
                "reference_color",
                "#FFFFFF"
            )
        )
        reference_color.pack(
            side="left",
            fill="x",
            expand=True
        )

        def choose_reference_color():
            from tkinter import colorchooser

            color = colorchooser.askcolor(
                title="Choose Verse Reference Color",
                initialcolor=reference_color.get()
            )

            if color and color[1]:
                reference_color.delete(0, tk.END)
                reference_color.insert(0, color[1])

        tk.Button(
            reference_row,
            text="COLOR",
            command=choose_reference_color,
            bg="#333333",
            fg="white",
            relief="flat"
        ).pack(
            side="left",
            padx=(8, 0)
        )

        # Reference font size
        tk.Label(
            scripture_frame,
            text="Reference Font Size",
            bg="#151515",
            fg="white"
        ).pack(anchor="w")

        reference_size = ttk.Combobox(
            scripture_frame,
            values=[
                "22",
                "26",
                "30",
                "34",
                "38",
                "42"
            ],
            state="readonly"
        )
        reference_size.set(
            str(
                self.settings.get(
                    "reference_font_size",
                    34
                )
            )
        )
        reference_size.pack(
            fill="x",
            pady=(5, 10)
        )

        reference_bold_var = tk.BooleanVar(
            value=self.settings.get(
                "reference_bold",
                True
            )
        )

        tk.Checkbutton(
            scripture_frame,
            text="Bold Verse Reference",
            variable=reference_bold_var,
            bg="#151515",
            fg="white",
            selectcolor="#333333",
            activebackground="#151515",
            activeforeground="white"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        # Live preview
        preview_window = {"window": None}

        def show_scripture_preview():
            from tkinter import colorchooser

            try:
                bg = scripture_bg.get().strip()
                txt = scripture_text.get().strip()
                ref_color = reference_color.get().strip()

                preview = tk.Toplevel(window)
                preview_window["window"] = preview

                preview.title(
                    "GREENBIBLE - Scripture Preview"
                )
                preview.geometry("900x500")
                preview.configure(bg=bg)

                ref_font = (
                    "Arial",
                    int(reference_size.get()),
                    "bold"
                    if reference_bold_var.get()
                    else "normal"
                )

                verse_font = (
                    "Arial",
                    int(scripture_size.get()),
                    "bold"
                    if scripture_bold_var.get()
                    else "normal"
                )

                ref_anchor = {
                    "top left": "w",
                    "top center": "center",
                    "top right": "e"
                }.get(
                    reference_position.get(),
                    "w"
                )

                ref_label = tk.Label(
                    preview,
                    text="John 3:16   KJV",
                    bg=bg,
                    fg=ref_color,
                    font=ref_font
                )

                ref_label.pack(
                    fill="x",
                    padx=30,
                    pady=(30, 10)
                )

                verse = tk.Label(
                    preview,
                    text=(
                        "For God so loved the world, "
                        "that he gave his only begotten Son, "
                        "that whosoever believeth in him "
                        "should not perish, but have "
                        "everlasting life."
                    ),
                    bg=bg,
                    fg=txt,
                    font=verse_font,
                    justify=scripture_align.get(),
                    anchor=scripture_align.get(),
                    wraplength=800
                )

                verse.pack(
                    expand=True,
                    fill="both",
                    padx=50,
                    pady=30
                )

                close_btn = tk.Button(
                    preview,
                    text="CLOSE PREVIEW",
                    command=preview.destroy,
                    bg="#333333",
                    fg="white",
                    relief="flat"
                )

                close_btn.pack(
                    pady=(0, 20)
                )

            except Exception as e:
                print(
                    "SCRIPTURE PREVIEW ERROR:",
                    e
                )

        def apply_scripture_style():
            try:
                bg = scripture_bg.get().strip()
                txt = scripture_text.get().strip()
                ref_color_value = reference_color.get().strip()

                # Validate colors through Tkinter
                test = tk.Toplevel(window)
                test.withdraw()

                try:
                    test.winfo_rgb(bg)
                    test.winfo_rgb(txt)
                    test.winfo_rgb(ref_color_value)
                finally:
                    test.destroy()

                self.settings["scripture_bg"] = bg
                self.settings["scripture_text"] = txt
                self.settings["scripture_font_size"] = int(
                    scripture_size.get()
                )
                self.settings["scripture_bold"] = (
                    scripture_bold_var.get()
                )
                self.settings["scripture_align"] = (
                    scripture_align.get()
                )
                self.settings["reference_position"] = (
                    reference_position.get()
                )
                self.settings["reference_color"] = (
                    ref_color_value
                )
                self.settings["reference_font_size"] = int(
                    reference_size.get()
                )
                self.settings["reference_bold"] = (
                    reference_bold_var.get()
                )

                # Apply to live NDI Scripture
                if hasattr(self, "ndi") and self.ndi:
                    try:
                        self.ndi.set_scripture_style(
                            background=bg,
                            text_color=txt,
                            font_size=int(
                                scripture_size.get()
                            ),
                            bold=scripture_bold_var.get(),
                            alignment=scripture_align.get(),
                            reference_color=ref_color_value,
                            reference_font_size=int(
                                reference_size.get()
                            ),
                            reference_bold=reference_bold_var.get(),
                            reference_position=reference_position.get()
                        )
                    except Exception as e:
                        print(
                            "NDI SCRIPTURE STYLE ERROR:",
                            e
                        )

                # Apply style to the GREENBIBLE Scripture display only
                try:
                    self.apply_scripture_display_style()
                except Exception as e:
                    print(
                        "GREENBIBLE SCRIPTURE STYLE ERROR:",
                        e
                    )

                Path(
                    self.settings_file
                ).write_text(
                    json.dumps(
                        self.settings,
                        indent=2
                    ),
                    encoding="utf-8"
                )

                print(
                    "SCRIPTURE PRESENTATION STYLE APPLIED"
                )

            except Exception as e:
                messagebox.showerror(
                    "Scripture Style",
                    "Invalid color or setting.\n\n"
                    + str(e)
                )

        tk.Button(
            scripture_frame,
            text="LIVE PREVIEW",
            command=show_scripture_preview,
            bg="#333333",
            fg="white",
            relief="flat",
            height=2
        ).pack(
            fill="x",
            pady=(5, 5)
        )

        tk.Button(
            scripture_frame,
            text="APPLY SCRIPTURE STYLE",
            command=apply_scripture_style,
            bg="#006633",
            fg="white",
            relief="flat",
            height=2
        ).pack(
            fill="x",
            pady=(0, 10)
        )

        # Save when the button is pressed.
        tk.Button(
            window,
            text="SAVE SETTINGS",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=10,
            command=save_settings
        ).pack(pady=12)

        # Also save automatically when the Settings window is closed.
        window.protocol(
            "WM_DELETE_WINDOW",
            save_settings
        )

    def open_themes(self):
        window = tk.Toplevel(self.root)
        window.title("GREENBIBLE - THEMES")
        window.geometry("500x500")
        window.configure(bg="#151515")

        tk.Label(
            window,
            text="GREENBIBLE THEMES",
            bg="#151515",
            fg="white",
            font=("Arial", 25, "bold")
        ).pack(pady=25)

        for theme_name in self.themes:
            tk.Button(
                window,
                text=theme_name,
                font=("Arial", 15, "bold"),
                width=25,
                pady=10,
                command=lambda name=theme_name:
                    self.select_theme(name, window)
            ).pack(pady=7)

    def select_theme(self, theme_name, window):
        self.current_theme = theme_name

        if theme_name == "Custom":
            background = colorchooser.askcolor(
                title="Choose Background Color"
            )[1]

            if background:
                self.themes["Custom"]["background"] = background

        window.destroy()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.build_interface()


if __name__ == "__main__":
    root = tk.Tk()
    app = GreenBibleInterface(root)

    def shutdown():
        app.stop_listening()
        if app.ndi:
            try:
                app.ndi.close()
            except Exception:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", shutdown)
    root.mainloop()



