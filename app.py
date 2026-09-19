from interface import GreenBibleInterface
import os, sqlite3, tempfile, threading, wave, tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import speech_recognition as sr
from smart_parser import extract_reference as smart_extract_reference, BOOKS

SAMPLE_RATE = 48000
RECORD_SECONDS = 6
KJV_DATABASE = "kjv.sqlite"
listening = False

def get_kjv_verse(book, chapter, verse):
    if not os.path.exists(KJV_DATABASE):
        raise FileNotFoundError("kjv.sqlite was not found in the GREENBIBLE folder.")
    with sqlite3.connect(KJV_DATABASE) as conn:
        row = conn.execute("SELECT text FROM verses WHERE book_id=? AND chapter=? AND number=?", (BOOKS[book], chapter, verse)).fetchone()
    return row[0] if row else None

def extract_reference(text):
    result = smart_extract_reference(text)
    if not result: return None
    parts = result.rsplit(" ", 1)
    if len(parts) != 2 or ":" not in parts[1]: return None
    book, ref = parts
    chapter, verse = ref.split(":", 1)
    try: return book, int(chapter), int(verse)
    except ValueError: return None

def record_audio():
    print("GREENBIBLE: Listening...")
    audio = sd.rec(int(RECORD_SECONDS*SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False); name=f.name; f.close()
    with wave.open(name, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE); w.writeframes(audio.tobytes())
    return name

def recognize_audio(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source: audio = r.record(source)
    return r.recognize_google(audio)

def show_reference(book, chapter, verse, text, spoken):
    reference_label.config(text=f"{book} {chapter}:{verse}")
    verse_text.config(text=text)
    status_label.config(text=f"● Listening  |  KJV  |  Heard: {spoken}")

def worker():
    global listening
    while listening:
        filename=None
        try:
            status_label.config(text="● Listening...")
            filename=record_audio()
            if not listening: break
            status_label.config(text="● Processing speech...")
            spoken=recognize_audio(filename)
            print("GREENBIBLE heard:", spoken)
            ref=extract_reference(spoken)
            if ref:
                book, chapter, verse=ref
                print(f"Reference detected: {book} {chapter}:{verse}")
                text=get_kjv_verse(book, chapter, verse)
                if text: root.after(0, show_reference, book, chapter, verse, text, spoken)
                else: status_label.config(text="Verse not found in KJV database.")
            else:
                print("No Bible reference detected:", spoken)
                status_label.config(text="● Listening... (No Bible reference detected)")
        except sr.UnknownValueError:
            status_label.config(text="● Listening... (Speech not understood)")
        except sr.RequestError:
            messagebox.showerror("GREENBIBLE", "Speech recognition needs an internet connection.")
            listening=False
        except Exception as e:
            print("GREENBIBLE error:", e); messagebox.showerror("GREENBIBLE", str(e)); listening=False
        finally:
            if filename and os.path.exists(filename):
                try: os.remove(filename)
                except OSError: pass
    root.after(0, stop_ui)

def start_listening():
    global listening
    if listening: return
    listening=True; listen_button.config(text="🎤 LISTENING..."); stop_button.config(state="normal"); status_label.config(text="● Listening...")
    threading.Thread(target=worker, daemon=True).start()

def stop_ui():
    listen_button.config(text="🎤 LISTEN"); stop_button.config(state="disabled"); status_label.config(text="Ready")

def stop_listening():
    global listening
    listening=False; stop_ui(); print("GREENBIBLE: Listening stopped.")

root=tk.Tk(); app=GreenBibleInterface(root); root.mainloop()


