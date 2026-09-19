import sqlite3

DB = "songs.sqlite"


def _connect():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            lyrics TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def load_songs():
    conn = _connect()

    rows = conn.execute(
        "SELECT title, lyrics FROM songs ORDER BY id"
    ).fetchall()

    conn.close()

    return {title: lyrics for title, lyrics in rows}


def save_song(title, lyrics):
    conn = _connect()

    conn.execute(
        """
        INSERT INTO songs (title, lyrics)
        VALUES (?, ?)
        ON CONFLICT(title)
        DO UPDATE SET lyrics = excluded.lyrics
        """,
        (title, lyrics)
    )

    conn.commit()
    conn.close()


def delete_song(title):
    conn = _connect()

    conn.execute(
        "DELETE FROM songs WHERE title = ?",
        (title,)
    )

    conn.commit()
    conn.close()