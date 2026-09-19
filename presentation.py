import tkinter as tk


class GreenBiblePresentation:
    def __init__(self, parent, on_close=None):
        self.parent = parent
        self.on_close = on_close
        self.fullscreen = False

        self.window = tk.Toplevel(parent)
        self.window.title("GREENBIBLE - LIVE PRESENTATION")
        self.window.geometry("1280x720")
        self.window.configure(bg="black")

        # Scripture reference
        self.reference = tk.Label(
            self.window,
            text="GREENBIBLE",
            bg="black",
            fg="white",
            font=("Arial", 34, "bold")
        )
        self.reference.pack(pady=(45, 5))

        # KJV label - yellow
        self.version = tk.Label(
            self.window,
            text="KJV",
            bg="black",
            fg="yellow",
            font=("Arial", 22, "bold")
        )
        self.version.pack(pady=(0, 15))

        # Scripture text
        self.verse = tk.Label(
            self.window,
            text="Waiting for Scripture...",
            bg="black",
            fg="white",
            font=("Arial", 38),
            wraplength=1100,
            justify="center"
        )
        self.verse.pack(expand=True, padx=70)

        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def show_verse(self, reference, text):
        if not self.window.winfo_exists():
            return

        self.reference.config(text=reference)
        self.verse.config(text=text)

    def toggle_fullscreen(self, event=None):
        if not self.window.winfo_exists():
            return

        self.fullscreen = not self.fullscreen
        self.window.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        if not self.window.winfo_exists():
            return

        self.fullscreen = False
        self.window.attributes("-fullscreen", False)

    def close(self):
        self.fullscreen = False

        if self.window.winfo_exists():
            self.window.destroy()

        if self.on_close:
            self.on_close()