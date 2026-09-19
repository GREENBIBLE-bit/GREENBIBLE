import tkinter as tk
from tkinter import messagebox, simpledialog

from song_store import load_songs, save_song, delete_song


# =========================================================
# GREENBIBLE SHARED SONG DATABASE
# =========================================================

SONGS_DATABASE = load_songs()

# Keep the original built-in songs available on first use.
if not SONGS_DATABASE:
    SONGS_DATABASE = {
        "Amazing Grace":
            "Amazing Grace\n"
            "Amazing grace! How sweet the sound\n"
            "That saved a wretch like me!\n"
            "I once was lost, but now am found;\n"
            "Was blind, but now I see.",

        "How Great Thou Art":
            "How Great Thou Art\n"
            "O Lord my God, when I in awesome wonder\n"
            "Consider all the worlds Thy Hands have made;\n"
            "I see the stars, I hear the rolling thunder."
    }

    for _title, _lyrics in SONGS_DATABASE.items():
        save_song(_title, _lyrics)


# =========================================================
# SONG DATABASE HELPERS
# =========================================================

def save_song_to_database(title, lyrics):
    SONGS_DATABASE[title] = lyrics
    save_song(title, lyrics)


def delete_song_from_database(title):
    SONGS_DATABASE.pop(title, None)
    delete_song(title)


class SongsWindow:
    def __init__(self, parent):
        self.parent = parent

        root = parent.root if hasattr(parent, "root") else parent

        self.window = tk.Toplevel(root)
        self.window.title("GREENBIBLE - SONGS")
        self.window.geometry("1100x750")
        self.window.minsize(950, 650)
        self.window.configure(bg="#151515")

        # =========================
        # TITLE
        # =========================
        tk.Label(
            self.window,
            text="GREENBIBLE SONGS",
            bg="#151515",
            fg="#00ff66",
            font=("Arial", 24, "bold")
        ).pack(fill="x", pady=12)

        # =========================
        # LINE CONTROL BAR
        # =========================
        controls = tk.Frame(
            self.window,
            bg="#101010",
            height=75
        )
        controls.pack(fill="x", padx=15, pady=5)
        controls.pack_propagate(False)

        tk.Label(
            controls,
            text="LIVE LINES:",
            bg="#101010",
            fg="white",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=(12, 5))

        self.line_count = tk.IntVar(value=2)

        tk.Radiobutton(
            controls,
            text="1 LINE",
            variable=self.line_count,
            value=1,
            bg="#101010",
            fg="white",
            selectcolor="#333333",
            activebackground="#101010",
            activeforeground="white",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            controls,
            text="2 LINES",
            variable=self.line_count,
            value=2,
            bg="#101010",
            fg="white",
            selectcolor="#333333",
            activebackground="#101010",
            activeforeground="white",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            controls,
            text="3 LINES",
            variable=self.line_count,
            value=3,
            bg="#101010",
            fg="white",
            selectcolor="#333333",
            activebackground="#101010",
            activeforeground="white",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="SHOW LIVE",
            command=self.show_song,
            bg="#008844",
            fg="white",
            activebackground="#00aa55",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=13,
            height=2
        ).pack(side="left", padx=8)

        tk.Button(
            controls,
            text="NEXT",
            command=self.next_lines,
            bg="#006699",
            fg="white",
            activebackground="#0088bb",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=10,
            height=2
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="CLEAR LIVE",
            command=self.clear_song,
            bg="#aa3333",
            fg="white",
            activebackground="#cc4444",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=13,
            height=2
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="EDIT",
            command=self.edit_song,
            bg="#555555",
            fg="white",
            activebackground="#777777",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=10,
            height=2
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="ADD SONG",
            command=self.add_song,
            bg="#008866",
            fg="white",
            activebackground="#00aa88",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=11,
            height=2
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="DELETE",
            command=self.delete_song,
            bg="#993333",
            fg="white",
            activebackground="#bb4444",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=10,
            height=2
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="CLOSE",
            command=self.window.destroy,
            font=("Arial", 12, "bold"),
            width=10,
            height=2
        ).pack(side="right", padx=8)

        # =========================
        # MAIN AREA
        # =========================
        main = tk.Frame(
            self.window,
            bg="#151515"
        )
        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        # =========================
        # LEFT - SONG LIST
        # =========================
        left = tk.Frame(
            main,
            bg="#1e1e1e",
            width=280
        )
        left.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )
        left.pack_propagate(False)

        tk.Label(
            left,
            text="SONGS",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.song_list = tk.Listbox(
            left,
            bg="#252525",
            fg="white",
            selectbackground="#00aa55",
            selectforeground="white",
            font=("Arial", 14)
        )
        self.song_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # =========================
        # RIGHT - LYRICS
        # =========================
        right = tk.Frame(
            main,
            bg="#1e1e1e"
        )
        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            right,
            text="LYRICS",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.lyrics = tk.Text(
            right,
            bg="#252525",
            fg="white",
            insertbackground="white",
            font=("Arial", 17),
            wrap="word"
        )
        self.lyrics.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # =========================
        # SHARED SONG DATA
        # =========================
        self.songs = SONGS_DATABASE

        for title in self.songs:
            self.song_list.insert(tk.END, title)

        self.song_list.bind(
            "<<ListboxSelect>>",
            self.select_song
        )

        # Current live position
        self.current_line = 0

    # =========================
    # SELECT SONG
    # =========================
    def select_song(self, event=None):
        selection = self.song_list.curselection()

        if not selection:
            return

        title = self.song_list.get(selection[0])

        self.lyrics.delete("1.0", tk.END)
        self.lyrics.insert("1.0", self.songs[title])

        self.current_line = 0

    # =========================
    # GET CLEAN LINES
    # =========================
    def get_lines(self):
        text = self.lyrics.get("1.0", tk.END).strip()

        lines = []

        for line in text.splitlines():
            line = line.strip()

            if line:
                lines.append(line)

        return lines

    # =========================
    # SHOW SELECTED LINES
    # =========================
    def show_song(self):
        selection = self.song_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select a song first."
            )
            return

        title = self.song_list.get(selection[0])
        lines = self.get_lines()

        if not lines:
            messagebox.showwarning(
                "GREENBIBLE",
                "There are no lyrics."
            )
            return

        count = self.line_count.get()

        start = self.current_line
        end = start + count

        live_lines = lines[start:end]

        if not live_lines:
            self.current_line = 0
            live_lines = lines[0:count]

        live_text = "\n".join(live_lines)

        try:
            if hasattr(self.parent, "show_song"):
                self.parent.show_song(title, live_text)

            elif hasattr(self.parent, "ndi") and self.parent.ndi:
                self.parent.ndi.update(title, live_text)

        except Exception as e:
            print("GREENBIBLE SONG SHOW ERROR:", e)

    # =========================
    # NEXT LINES
    # =========================
    def next_lines(self):
        selection = self.song_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select a song first."
            )
            return

        lines = self.get_lines()

        if not lines:
            return

        count = self.line_count.get()

        self.current_line += count

        if self.current_line >= len(lines):
            self.current_line = 0

        self.show_song()

    # =========================
    # CLEAR LIVE
    # =========================
    def clear_song(self):
        try:
            if hasattr(self.parent, "clear_song"):
                self.parent.clear_song()
                return

            if hasattr(self.parent, "scripture_text"):
                self.parent.scripture_text.config(state="normal")
                self.parent.scripture_text.delete("1.0", tk.END)
                self.parent.scripture_text.insert(
                    "1.0",
                    "Waiting for Scripture..."
                )
                self.parent.scripture_text.config(state="disabled")

            if hasattr(self.parent, "ndi") and self.parent.ndi:
                self.parent.ndi.update(
                    "GREENBIBLE",
                    "Waiting for content..."
                )

        except Exception as e:
            print("GREENBIBLE SONG CLEAR ERROR:", e)

    # =========================
    # EDIT SONG
    # =========================
    def edit_song(self):
        selection = self.song_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select a song first."
            )
            return

        index = selection[0]
        original_title = self.song_list.get(index)
        original_content = self.songs.get(original_title, "")

        editor = tk.Toplevel(self.window)
        editor.title("GREENBIBLE - SONG EDITOR")
        editor.geometry("1100x750")
        editor.minsize(800, 600)
        editor.configure(bg="#111111")
        editor.transient(self.window)
        editor.grab_set()

        # TOP AREA
        top = tk.Frame(editor, bg="#111111")
        top.pack(
            side="top",
            fill="x",
            padx=20,
            pady=15
        )

        tk.Label(
            top,
            text="SONG TITLE",
            fg="white",
            bg="#111111",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        title_entry = tk.Entry(
            top,
            font=("Arial", 17),
            bg="white",
            fg="black"
        )
        title_entry.pack(fill="x")
        title_entry.insert(0, original_title)

        tk.Label(
            top,
            text="SONG CONTENT / LYRICS",
            fg="white",
            bg="#111111",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(15, 5))

        # BOTTOM BUTTON BAR FIRST
        buttons = tk.Frame(
            editor,
            bg="#111111",
            height=75
        )
        buttons.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=10
        )
        buttons.pack_propagate(False)

        # LYRICS AREA
        content = tk.Text(
            editor,
            font=("Arial", 20),
            bg="white",
            fg="black",
            insertbackground="black",
            wrap="word"
        )
        content.pack(
            side="top",
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )
        content.insert("1.0", original_content)

        def save_song():
            new_title = title_entry.get().strip()
            new_content = content.get(
                "1.0",
                tk.END
            ).strip()

            if not new_title:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter a song title.",
                    parent=editor
                )
                return

            if not new_content:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter the song lyrics.",
                    parent=editor
                )
                return

            if (
                new_title != original_title
                and new_title in self.songs
            ):
                messagebox.showwarning(
                    "GREENBIBLE",
                    "A song with this title already exists.",
                    parent=editor
                )
                return

            if original_title != new_title:
                self.songs.pop(
                    original_title,
                    None
                )

            self.songs[new_title] = new_content

            self.song_list.delete(index)
            self.song_list.insert(
                index,
                new_title
            )
            self.song_list.selection_clear(
                0,
                tk.END
            )
            self.song_list.selection_set(index)
            self.song_list.activate(index)
            self.song_list.see(index)

            self.lyrics.delete(
                "1.0",
                tk.END
            )
            self.lyrics.insert(
                "1.0",
                new_content
            )
            self.current_line = 0

            messagebox.showinfo(
                "GREENBIBLE",
                "Song saved successfully.",
                parent=editor
            )

            editor.destroy()

        tk.Button(
            buttons,
            text="SAVE SONG",
            command=save_song,
            bg="#1976d2",
            fg="white",
            activebackground="#2196f3",
            activeforeground="white",
            font=("Arial", 14, "bold"),
            width=16,
            height=2
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            buttons,
            text="CANCEL",
            command=editor.destroy,
            bg="#555555",
            fg="white",
            activebackground="#777777",
            activeforeground="white",
            font=("Arial", 14, "bold"),
            width=12,
            height=2
        ).pack(
            side="right",
            padx=5
        )

    def add_song(self):
        editor = tk.Toplevel(self.window)
        editor.title("GREENBIBLE - ADD SONG")
        editor.geometry("1100x750")
        editor.minsize(800, 600)
        editor.configure(bg="#111111")
        editor.transient(self.window)
        editor.grab_set()

        # TOP AREA
        top = tk.Frame(editor, bg="#111111")
        top.pack(
            side="top",
            fill="x",
            padx=20,
            pady=15
        )

        tk.Label(
            top,
            text="SONG TITLE",
            fg="white",
            bg="#111111",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        title_entry = tk.Entry(
            top,
            font=("Arial", 17),
            bg="white",
            fg="black"
        )
        title_entry.pack(fill="x")

        tk.Label(
            top,
            text="SONG CONTENT / LYRICS",
            fg="white",
            bg="#111111",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(15, 5))

        # BOTTOM BUTTON BAR FIRST
        buttons = tk.Frame(
            editor,
            bg="#111111",
            height=75
        )
        buttons.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=10
        )
        buttons.pack_propagate(False)

        # LYRICS AREA
        content = tk.Text(
            editor,
            font=("Arial", 20),
            bg="white",
            fg="black",
            insertbackground="black",
            wrap="word"
        )
        content.pack(
            side="top",
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        def save_new_song():
            title = title_entry.get().strip()
            lyrics = content.get(
                "1.0",
                tk.END
            ).strip()

            if not title:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter a song title.",
                    parent=editor
                )
                return

            if not lyrics:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter the song lyrics.",
                    parent=editor
                )
                return

            if title in self.songs:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "A song with this title already exists.",
                    parent=editor
                )
                return

            self.songs[title] = lyrics

            self.song_list.insert(
                tk.END,
                title
            )

            last_index = self.song_list.size() - 1

            self.song_list.selection_clear(
                0,
                tk.END
            )
            self.song_list.selection_set(
                last_index
            )
            self.song_list.activate(
                last_index
            )
            self.song_list.see(
                last_index
            )

            self.lyrics.delete(
                "1.0",
                tk.END
            )
            self.lyrics.insert(
                "1.0",
                lyrics
            )
            self.current_line = 0

            messagebox.showinfo(
                "GREENBIBLE",
                "Song added successfully.",
                parent=editor
            )

            editor.destroy()

        tk.Button(
            buttons,
            text="SAVE SONG",
            command=save_new_song,
            bg="#1976d2",
            fg="white",
            activebackground="#2196f3",
            activeforeground="white",
            font=("Arial", 14, "bold"),
            width=16,
            height=2
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            buttons,
            text="CANCEL",
            command=editor.destroy,
            bg="#555555",
            fg="white",
            activebackground="#777777",
            activeforeground="white",
            font=("Arial", 14, "bold"),
            width=12,
            height=2
        ).pack(
            side="right",
            padx=5
        )

    def delete_song(self):
        selection = self.song_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select a song first."
            )
            return

        index = selection[0]
        title = self.song_list.get(index)

        answer = messagebox.askyesno(
            "GREENBIBLE",
            f'Delete "{title}"?'
        )

        if not answer:
            return

        self.songs.pop(title, None)

        self.song_list.delete(index)

        self.lyrics.delete("1.0", tk.END)

        remaining = self.song_list.size()

        if remaining > 0:
            new_index = min(index, remaining - 1)

            self.song_list.selection_set(new_index)
            self.song_list.activate(new_index)
            self.song_list.see(new_index)

            selected_title = self.song_list.get(new_index)

            self.lyrics.insert(
                "1.0",
                self.songs.get(selected_title, "")
            )

        self.current_line = 0

        messagebox.showinfo(
            "GREENBIBLE",
            "Song deleted successfully."
        )


def open_songs(parent):
    SongsWindow(parent)