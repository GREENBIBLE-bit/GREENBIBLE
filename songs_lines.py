import tkinter as tk
from tkinter import messagebox, simpledialog


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
        # SONG DATA
        # =========================
        self.songs = {
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

        title = self.song_list.get(selection[0])

        new_title = simpledialog.askstring(
            "EDIT SONG",
            "Song title:",
            initialvalue=title,
            parent=self.window
        )

        if not new_title:
            return

        current_lyrics = self.lyrics.get(
            "1.0",
            tk.END
        ).strip()

        self.songs.pop(title)
        self.songs[new_title] = current_lyrics

        self.song_list.delete(selection[0])
        self.song_list.insert(
            selection[0],
            new_title
        )

        self.song_list.selection_set(selection[0])

        messagebox.showinfo(
            "GREENBIBLE",
            "Song updated successfully."
        )


def open_songs(parent):
    SongsWindow(parent)