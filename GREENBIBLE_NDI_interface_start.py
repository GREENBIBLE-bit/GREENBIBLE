import os
import sqlite3
import tempfile
import threading
import wave
import tkinter as tk

import sounddevice as sd
import speech_recognition as sr

from smart_parser import extract_reference as smart_extract_reference, BOOKS
from presentation import GreenBiblePresentation
import ndi_renderer


SAMPLE_RATE = 48000
RECORD_SECONDS = 6
KJV_DATABASE = "kjv.sqlite"

listening = False
presentation = None

current_book = None
current_chapter = None
current_verse = None

def get_kjv_verse(book, chapter, verse):
    with sqlite3.connect(KJV_DATABASE) as connection:
        row = connection.execute(
            """
            SELECT text
            FROM verses
            WHERE book_id=? AND chapter=? AND number=?
            """,
            (BOOKS[book], chapter, verse)
        ).fetchone()

    return row[0] if row else None


def extract_reference(text):
    result = smart_extract_reference(text)

    if not result:
        return None

    parts = result.rsplit(" ", 1)

    if len(parts) != 2:
        return None

    book = parts[0]
    reference = parts[1]

    if ":" not in reference:
        return None

    chapter, verse = reference.split(":", 1)

    try:
        return book, int(chapter), int(verse)
    except ValueError:
        return None


def record_audio():
    print("GREENBIBLE: Listening...")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    temp = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    filename = temp.name
    temp.close()

    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio.tobytes())

    return filename


def recognize_audio(filename):
    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    return recognizer.recognize_google(audio)


def update_presentation(book, chapter, verse, text):
    global presentation, current_book, current_chapter, current_verse

    current_book = book
    current_chapter = chapter
    current_verse = verse

    reference = f"{book} {chapter}:{verse}"

    if presentation is None:
        presentation = GreenBiblePresentation(root)

    presentation.show_verse(reference, text)
    ndi_renderer.update(reference, text)

    if presentation.window.winfo_exists():
        presentation.window.lift()


def navigate_verse(direction):
    global current_book, current_chapter, current_verse

    if not current_book:
        print("GREENBIBLE: No current Scripture.")
        return

    book_id = BOOKS[current_book]

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
                    current_chapter,
                    current_chapter,
                    current_verse
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
                    current_chapter,
                    current_chapter,
                    current_verse
                )
            ).fetchone()

    if not row:
        print("GREENBIBLE: No more verses in this direction.")
        return

    chapter, verse, text = row

    print(
        f"GREENBIBLE navigation: "
        f"{current_book} {chapter}:{verse}"
    )

    root.after(
        0,
        update_presentation,
        current_book,
        chapter,
        verse,
        text
    )


def next_verse():
    navigate_verse("next")


def previous_verse():
    navigate_verse("previous")

def previous_verse():
    navigate_verse("previous")


def go_to_verse(verse_number):
    global current_book, current_chapter

    if not current_book:
        print("GREENBIBLE: No current Scripture.")
        return

    try:
        verse_number = int(verse_number)
    except ValueError:
        return

    text = get_kjv_verse(
        current_book,
        current_chapter,
        verse_number
    )

    if not text:
        print(
            f"GREENBIBLE: Verse not found: "
            f"{current_book} {current_chapter}:{verse_number}"
        )
        return

    print(
        f"GREENBIBLE navigation: "
        f"{current_book} {current_chapter}:{verse_number}"
    )

    root.after(
        0,
        update_presentation,
        current_book,
        current_chapter,
        verse_number,
        text
    )

def listen_loop():
    global listening

    while listening:

        filename = None

        try:

            filename = record_audio()

            if not listening:
                break

            text = recognize_audio(filename)

            print("GREENBIBLE heard:", text)
            command = text.lower().strip()

            if command in (
                "next verse",
                "next verses",
                "go to next verse"
            ):
                print("GREENBIBLE command: NEXT VERSE")
                root.after(0, next_verse)
                continue

            if command in (
                "previous verse",
                "previous verses",
                "go to previous verse",
                "last verse"
            ):
                print("GREENBIBLE command: PREVIOUS VERSE")
                root.after(0, previous_verse)
                continue
            result = extract_reference(text)

            if result:

                book, chapter, verse = result

                print(
                    f"Reference detected: "
                    f"{book} {chapter}:{verse}"
                )

                kjv_text = get_kjv_verse(
                    book,
                    chapter,
                    verse
                )

                if kjv_text:

                    root.after(
                        0,
                        update_presentation,
                        book,
                        chapter,
                        verse,
                        kjv_text
                    )

                else:

                    print(
                        "Verse not found in KJV database:"
                        f" {book} {chapter}:{verse}"
                    )

            else:

                print(
                    "No Bible reference detected:",
                    text
                )

        except sr.UnknownValueError:

            print(
                "GREENBIBLE: Speech not understood."
            )

        except sr.RequestError:

            print(
                "GREENBIBLE: Internet connection required."
            )

            listening = False

        except Exception as error:

            print(
                "GREENBIBLE error:",
                error
            )

            listening = False

        finally:

            if filename and os.path.exists(filename):

                try:
                    os.remove(filename)
                except OSError:
                    pass

    print("GREENBIBLE: Listening stopped.")


def start_listening():

    global listening

    if listening:
        return

    listening = True

    status_label.config(
        text="● LISTENING..."
    )

    listen_button.config(
        text="🎤 LISTENING..."
    )

    threading.Thread(
        target=listen_loop,
        daemon=True
    ).start()


def stop_listening():

    global listening

    listening = False

    status_label.config(
        text="READY"
    )

    listen_button.config(
        text="🎤 LISTEN"
    )


def open_presentation():

    global presentation

    if presentation is None:
        presentation = GreenBiblePresentation(root)
    else:
        presentation.window.lift()


root = tk.Tk()

ndi_renderer.start()

root.title(
    "GREENBIBLE - LIVE"
)

root.geometry(
    "1100x700"
)

root.configure(
    bg="#111111"
)


title_label = tk.Label(
    root,
    text="GREENBIBLE",
    bg="#111111",
    fg="white",
    font=("Arial", 36, "bold")
)

title_label.pack(
    pady=(40, 10)
)


subtitle_label = tk.Label(
    root,
    text="VOICE BIBLE • KJV • LIVE PRESENTATION",
    bg="#111111",
    fg="white",
    font=("Arial", 16)
)

subtitle_label.pack(
    pady=10
)


status_label = tk.Label(
    root,
    text="READY",
    bg="#111111",
    fg="white",
    font=("Arial", 18, "bold")
)

status_label.pack(
    pady=35
)


button_frame = tk.Frame(
    root,
    bg="#111111"
)

button_frame.pack(
    pady=30
)


listen_button = tk.Button(
    button_frame,
    text="🎤 LISTEN",
    command=start_listening,
    font=("Arial", 20, "bold"),
    padx=40,
    pady=20
)

listen_button.pack(
    side="left",
    padx=15
)


stop_button = tk.Button(
    button_frame,
    text="■ STOP",
    command=stop_listening,
    font=("Arial", 20, "bold"),
    padx=40,
    pady=20
)

stop_button.pack(
    side="left",
    padx=15
)


presentation_button = tk.Button(
    button_frame,
    text="🖥 LIVE PRESENTATION",
    command=open_presentation,
    font=("Arial", 20, "bold"),
    padx=30,
    pady=20
)

presentation_button.pack(
    side="left",
    padx=15
)


info_label = tk.Label(
    root,
    text="Say a Bible reference such as: John 3:16",
    bg="#111111",
    fg="white",
    font=("Arial", 15)
)

info_label.pack(
    pady=40
)


root.bind(
    "<F5>",
    lambda event: start_listening()
)

root.bind(
    "<F6>",
    lambda event: stop_listening()
)

root.protocol("WM_DELETE_WINDOW", lambda: (ndi_renderer.close(), root.destroy()))

root.mainloop()