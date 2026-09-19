import re
import sqlite3
import os

BOOKS = {
    "Genesis": 1, "Exodus": 2, "Leviticus": 3, "Numbers": 4, "Deuteronomy": 5,
    "Joshua": 6, "Judges": 7, "Ruth": 8, "1 Samuel": 9, "2 Samuel": 10,
    "1 Kings": 11, "2 Kings": 12, "1 Chronicles": 13, "2 Chronicles": 14,
    "Ezra": 15, "Nehemiah": 16, "Esther": 17, "Job": 18, "Psalm": 19,
    "Proverbs": 20, "Ecclesiastes": 21, "Song of Solomon": 22, "Isaiah": 23,
    "Jeremiah": 24, "Lamentations": 25, "Ezekiel": 26, "Daniel": 27,
    "Hosea": 28, "Joel": 29, "Amos": 30, "Obadiah": 31, "Jonah": 32,
    "Micah": 33, "Nahum": 34, "Habakkuk": 35, "Zephaniah": 36,
    "Haggai": 37, "Zechariah": 38, "Malachi": 39, "Matthew": 40,
    "Mark": 41, "Luke": 42, "John": 43, "Acts": 44, "Romans": 45,
    "1 Corinthians": 46, "2 Corinthians": 47, "Galatians": 48, "Ephesians": 49,
    "Philippians": 50, "Colossians": 51, "1 Thessalonians": 52,
    "2 Thessalonians": 53, "1 Timothy": 54, "2 Timothy": 55, "Titus": 56,
    "Philemon": 57, "Hebrews": 58, "James": 59, "1 Peter": 60, "2 Peter": 61,
    "1 John": 62, "2 John": 63, "3 John": 64, "Jude": 65, "Revelation": 66,
}

ALIASES = {
    "revelations": "revelation", "revell": "revelation", "revellation": "revelation",
    "revel": "revelation", "rev": "revelation", "psalms": "psalm",
    "max": "mark", "marc": "mark", "mar": "mark", "proctor": "proverbs",
    "proverb": "proverbs", "ex": "exodus", "exod": "exodus",
    "corinthian": "corinthians", "thessalonian": "thessalonians", "roman": "romans",
}
ORDINALS = {"first":"1", "1st":"1", "one":"1", "second":"2", "2nd":"2", "two":"2", "third":"3", "3rd":"3", "three":"3"}

def normalize_text(text):
    text = text.lower().strip()
    for old, new in ALIASES.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    for old, new in ORDINALS.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    text = re.sub(r"\b(chapter|verse|please|open|show|read|display|go to|find|turn to)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def database_reference_exists(book_id, chapter, verse=None):
    if not os.path.exists("kjv.sqlite"):
        return False
    with sqlite3.connect("kjv.sqlite") as conn:
        if verse is None:
            row = conn.execute("SELECT 1 FROM verses WHERE book_id=? AND chapter=? LIMIT 1", (book_id, chapter)).fetchone()
        else:
            row = conn.execute("SELECT 1 FROM verses WHERE book_id=? AND chapter=? AND number=? LIMIT 1", (book_id, chapter, verse)).fetchone()
    return row is not None

def find_book(text):
    for book in sorted(BOOKS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(book.lower()) + r"\b", text):
            return book
    return None

def extract_reference(text):
    original = text
    text = normalize_text(text)
    book = find_book(text)
    if not book:
        return None
    book_id = BOOKS[book]
    m = re.search(r"\b" + re.escape(book.lower()) + r"\s+(\d{1,3})\s*:\s*(\d{1,3})\b", text)
    if m:
        chapter, verse = int(m.group(1)), int(m.group(2))
        if database_reference_exists(book_id, chapter, verse):
            return f"{book} {chapter}:{verse}"
    m = re.search(r"\b" + re.escape(book.lower()) + r"\s+(\d{1,3})\b", text)
    if m:
        digits = m.group(1)
        n = int(digits)
        if database_reference_exists(book_id, n):
            return f"{book} {n}"
        for split in range(1, len(digits)):
            chapter, verse = int(digits[:split]), int(digits[split:])
            if database_reference_exists(book_id, chapter, verse):
                return f"{book} {chapter}:{verse}"
    return None
