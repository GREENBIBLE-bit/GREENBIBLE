import tkinter as tk
import sqlite3
import tempfile
import threading
import wave
import os
from tkinter import ttk, colorchooser

import sounddevice as sd
import speech_recognition as sr

from smart_parser import extract_reference as smart_extract_reference
from smart_parser import BOOKS as SMART_BOOKS
import ndi_renderer
from presentation import GreenBiblePresentation


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

        self.settings = {
            "microphone": "Default Microphone",
            "listen_time": "6 seconds",
            "bible_version": "KJV",
            "ndi_name": "GREENBIBLE",
            "resolution": "1280x720",
        }

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

        # Start the existing native NDI renderer.
        try:
            self.ndi = ndi_renderer.NDIRenderer(
                source_name=self.settings["ndi_name"],
                width=1280,
                height=720,
                fps=30
            )
            self.ndi.start()
            print("GREENBIBLE NDI: ACTIVE")
            print("GREENBIBLE NDI SOURCE:", self.settings["ndi_name"])
        except Exception as e:
            self.ndi = None
            print("GREENBIBLE NDI ERROR:", e)

        self.build_interface()

    def build_interface(self):
        theme = self.themes[self.current_theme]

        self.root.configure(bg=theme["background"])

        header = tk.Frame(
            self.root,
            bg=theme["background"]
        )
        header.pack(fill="x", pady=(20, 5))

        tk.Label(
            header,
            text="GREENBIBLE",
            bg=theme["background"],
            fg=theme["text"],
            font=("Arial", 32, "bold")
        ).pack()

        tk.Label(
            header,
            text="VOICE BIBLE  |  KJV  |  NDI LIVE",
            bg=theme["background"],
            fg=theme["text"],
            font=("Arial", 14)
        ).pack(pady=3)

        main = tk.Frame(
            self.root,
            bg=theme["background"]
        )
        main.pack(fill="both", expand=True, padx=25, pady=10)

        left = tk.Frame(
            main,
            bg=theme["background"],
            width=400
        )
        left.pack(
            side="left",
            fill="y",
            padx=(0, 20)
        )

        right = tk.Frame(
            main,
            bg="#000000",
            bd=2,
            relief="solid"
        )
        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            left,
            text="NDI: READY",
            bg=theme["background"],
            fg="#00ff66",
            font=("Arial", 15, "bold")
        ).pack(pady=(15, 15))

        self.reference = tk.Label(
            left,
            text="No Scripture selected",
            bg=theme["background"],
            fg=theme["accent"],
            font=("Arial", 24, "bold"),
            wraplength=350
        )
        self.reference.pack(pady=15)

        self.status = tk.Label(
            left,
            text="READY",
            bg=theme["background"],
            fg=theme["text"],
            font=("Arial", 18, "bold")
        )
        self.status.pack(pady=10)

        button_frame = tk.Frame(
            left,
            bg=theme["background"]
        )
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="LISTEN",
            font=("Arial", 16, "bold"),
            padx=25,
            pady=14,
            command=self.start_listening
        ).pack(fill="x", pady=5)

        tk.Button(
            button_frame,
            text="STOP",
            font=("Arial", 16, "bold"),
            padx=25,
            pady=14,
            command=self.stop_listening
        ).pack(fill="x", pady=5)

        tk.Button(
            button_frame,
            text="LIVE PRESENTATION",
            font=("Arial", 16, "bold"),
            padx=20,
            pady=14,
            command=self.open_live_presentation
        ).pack(fill="x", pady=5)

        tk.Button(
            button_frame,
            text="TEST SCRIPTURE",
            font=("Arial", 16, "bold"),
            padx=20,
            pady=14,
            command=self.test_scripture
        ).pack(fill="x", pady=5)

        tk.Button(
            left,
            text="SETTINGS",
            font=("Arial", 14, "bold"),
            padx=25,
            pady=10,
            command=self.open_settings
        ).pack(pady=(15, 5))

        tk.Button(
            left,
            text="THEMES",
            font=("Arial", 14, "bold"),
            padx=25,
            pady=10,
            command=self.open_themes
        ).pack(pady=5)

        tk.Label(
            right,
            text="LIVE PREVIEW",
            bg="#000000",
            fg="#00ff66",
            font=("Arial", 15, "bold")
        ).pack(pady=(15, 5))

        self.preview_reference = tk.Label(
            right,
            text="John 3:16",
            bg="#000000",
            fg="white",
            font=("Arial", 30, "bold")
        )
        self.preview_reference.pack(pady=(20, 2))

        self.preview_version = tk.Label(
            right,
            text="KJV",
            bg="#000000",
            fg="yellow",
            font=("Arial", 20, "bold")
        )
        self.preview_version.pack(pady=(0, 15))

        self.preview_verse = tk.Label(
            right,
            text="Waiting for Scripture...",
            bg="#000000",
            fg="white",
            font=("Arial", 27),
            wraplength=700,
            justify="center"
        )
        self.preview_verse.pack(
            expand=True,
            padx=40,
            pady=20
        )

        tk.Label(
            self.root,
            text="Say a Bible reference such as: John 3:16",
            bg=theme["background"],
            fg="#AAAAAA",
            font=("Arial", 13)
        ).pack(pady=8)

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
        recognizer = sr.Recognizer()
        seconds = self._listen_seconds()

        while not self.stop_event.is_set():
            try:
                print("GREENBIBLE: Listening...")

                frames = int(48000 * seconds)
                audio_data = sd.rec(
                    frames,
                    samplerate=48000,
                    channels=1,
                    dtype="int16",
                    device=1
                )
                sd.wait()

                if self.stop_event.is_set():
                    break

                temp = tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False
                )
                temp.close()

                with wave.open(temp.name, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(48000)
                    wav_file.writeframes(audio_data.tobytes())

                try:
                    with sr.AudioFile(temp.name) as source:
                        audio = recognizer.record(source)

                    text = recognizer.recognize_google(audio)
                    print("GREENBIBLE heard:", text)

                    command = text.lower().strip()

                    if command in (
                        "next verse",
                        "next verses",
                        "go to next verse"
                    ):
                        print("GREENBIBLE command: NEXT VERSE")
                        self.root.after(0, self.next_verse)
                        continue

                    if command in (
                        "previous verse",
                        "previous verses",
                        "go to previous verse",
                        "last verse"
                    ):
                        print("GREENBIBLE command: PREVIOUS VERSE")
                        self.root.after(0, self.previous_verse)
                        continue

                    result = smart_extract_reference(text)

                    if result:
                        reference = result

                        # Handle parsers that return a tuple/list.
                        if isinstance(result, (tuple, list)):
                            if len(result) >= 3:
                                reference = f"{result[0]} {result[1]}:{result[2]}"
                            elif len(result) == 1:
                                reference = result[0]

                        reference = str(reference).strip()
                        parsed = self.parse_reference_text(reference)

                        if parsed:
                            book, chapter, verse = parsed
                            print(
                                f"Reference detected: "
                                f"{book} {chapter}:{verse}"
                            )
                            self.root.after(
                                0,
                                self.load_scripture,
                                book,
                                chapter,
                                verse
                            )
                        else:
                            print(
                                "GREENBIBLE: Parser returned:",
                                reference
                            )

                except sr.UnknownValueError:
                    print("GREENBIBLE: Could not understand audio.")
                except sr.RequestError as e:
                    print("GREENBIBLE Google ERROR:", e)
                finally:
                    try:
                        os.remove(temp.name)
                    except OSError:
                        pass

            except Exception as e:
                print("GREENBIBLE voice ERROR:", e)
                break

        self.voice_running = False
        self.root.after(0, lambda: self.status.config(text="READY"))

    def parse_reference_text(self, reference):
        import re

        match = re.search(
            r"^(.+?)\s+(\d+):(\d+)$",
            reference.strip()
        )

        if not match:
            return None

        book = match.group(1).strip()
        chapter = int(match.group(2))
        verse = int(match.group(3))

        if book not in BOOKS:
            return None

        return book, chapter, verse

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

    def show_scripture(self, book, chapter, verse, text):
        reference = f"{book} {chapter}:{verse}"

        self.reference.config(text=reference)
        self.status.config(text="SCRIPTURE LOADED")
        self.preview_reference.config(text=reference)
        self.preview_version.config(text="KJV")
        self.preview_verse.config(text=text)

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
        window.geometry("600x600")
        window.configure(bg="#151515")

        tk.Label(
            window,
            text="GREENBIBLE SETTINGS",
            bg="#151515",
            fg="white",
            font=("Arial", 25, "bold")
        ).pack(pady=20)

        frame = tk.Frame(window, bg="#151515")
        frame.pack(fill="both", expand=True, padx=40)

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

        def save_settings():
            self.settings["microphone"] = microphone.get()
            self.settings["listen_time"] = listen_time.get()
            self.settings["bible_version"] = bible_version.get()
            self.settings["ndi_name"] = ndi_name.get()
            self.settings["resolution"] = resolution.get()
            window.destroy()

        tk.Button(
            window,
            text="SAVE SETTINGS",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=10,
            command=save_settings
        ).pack(pady=20)

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