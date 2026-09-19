import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os


ANNOUNCEMENTS_FILE = "announcements.json"

class AnnouncementWindow:
    def __init__(self, parent):
        self.parent = parent

        root = parent.root if hasattr(parent, "root") else parent

        self.window = tk.Toplevel(root)
        self.window.title("GREENBIBLE - ANNOUNCEMENTS")
        self.window.geometry("1100x750")
        self.window.minsize(950, 650)
        self.window.configure(bg="#151515")

        # TITLE
        tk.Label(
            self.window,
            text="GREENBIBLE ANNOUNCEMENTS",
            bg="#151515",
            fg="#00ff66",
            font=("Arial", 24, "bold")
        ).pack(fill="x", pady=12)

        # CONTROL BAR
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
            command=self.show_announcement,
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
            command=self.clear_announcement,
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
            command=self.edit_announcement,
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
            text="ADD",
            command=self.add_announcement,
            bg="#7755aa",
            fg="white",
            activebackground="#9966cc",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            width=9,
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

        # MAIN AREA
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

        # LEFT - ANNOUNCEMENT LIST
        left = tk.Frame(
            main,
            bg="#1e1e1e",
            width=300
        )
        left.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )
        left.pack_propagate(False)

        tk.Label(
            left,
            text="ANNOUNCEMENTS",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.announcement_list = tk.Listbox(
            left,
            bg="#252525",
            fg="white",
            selectbackground="#00aa55",
            selectforeground="white",
            font=("Arial", 14)
        )
        self.announcement_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # RIGHT - CONTENT
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
            text="ANNOUNCEMENT CONTENT",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.content = tk.Text(
            right,
            bg="#252525",
            fg="white",
            insertbackground="white",
            font=("Arial", 17),
            wrap="word"
        )
        self.content.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.announcements = self.load_announcements()

        for title in self.announcements:
            self.announcement_list.insert(
                tk.END,
                title
            )

        self.announcement_list.bind(
            "<<ListboxSelect>>",
            self.select_announcement
        )

        self.current_line = 0

    # SELECT ANNOUNCEMENT
    def select_announcement(self, event=None):
        selection = self.announcement_list.curselection()

        if not selection:
            return

        title = self.announcement_list.get(selection[0])

        self.content.delete("1.0", tk.END)
        self.content.insert(
            "1.0",
            self.announcements[title]
        )

        self.current_line = 0

    # GET NON-EMPTY LINES
    def get_lines(self):
        text = self.content.get(
            "1.0",
            tk.END
        ).strip()

        lines = []

        for line in text.splitlines():
            line = line.strip()

            if line:
                lines.append(line)

        return lines

    # SHOW LIVE
    def show_announcement(self):
        selection = self.announcement_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select an announcement first."
            )
            return

        title = self.announcement_list.get(selection[0])
        lines = self.get_lines()

        if not lines:
            messagebox.showwarning(
                "GREENBIBLE",
                "There is no announcement content."
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
            if hasattr(self.parent, "show_announcement"):
                self.parent.show_announcement(
                    title,
                    live_text
                )

            elif hasattr(self.parent, "show_song"):
                self.parent.show_song(
                    title,
                    live_text
                )

            elif hasattr(self.parent, "ndi") and self.parent.ndi:
                self.parent.ndi.update(
                    title,
                    live_text
                )

        except Exception as e:
            print(
                "GREENBIBLE ANNOUNCEMENT SHOW ERROR:",
                e
            )

    # NEXT
    def next_lines(self):
        selection = self.announcement_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select an announcement first."
            )
            return

        lines = self.get_lines()

        if not lines:
            return

        count = self.line_count.get()

        self.current_line += count

        if self.current_line >= len(lines):
            self.current_line = 0

        self.show_announcement()

    # CLEAR LIVE
    def clear_announcement(self):
        try:
            if hasattr(
                self.parent,
                "clear_announcement"
            ):
                self.parent.clear_announcement()
                return

            if hasattr(
                self.parent,
                "scripture_text"
            ):
                self.parent.scripture_text.config(
                    state="normal"
                )

                self.parent.scripture_text.delete(
                    "1.0",
                    tk.END
                )

                self.parent.scripture_text.insert(
                    "1.0",
                    "Waiting for Scripture..."
                )

                self.parent.scripture_text.config(
                    state="disabled"
                )

            if hasattr(
                self.parent,
                "ndi"
            ) and self.parent.ndi:
                self.parent.ndi.update(
                    "GREENBIBLE",
                    "Waiting for content..."
                )

        except Exception as e:
            print(
                "GREENBIBLE ANNOUNCEMENT CLEAR ERROR:",
                e
            )

    def load_announcements(self):
        default_announcements = {
            "Sunday Service":
                "Sunday Service\n"
                "Join us this Sunday for a powerful time in God's presence.\n"
                "Service starts at 9:00 AM.",

            "Prayer Meeting":
                "Prayer Meeting\n"
                "Join us for our weekly prayer meeting.\n"
                "Come and let us seek the Lord together.",

            "Bible Study":
                "Bible Study\n"
                "Our weekly Bible Study is coming up.\n"
                "Bring your Bible and notebook."
        }

        if os.path.exists(ANNOUNCEMENTS_FILE):
            try:
                with open(
                    ANNOUNCEMENTS_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    return data

            except Exception:
                pass

        return default_announcements


    def save_announcements(self):
        try:
            with open(
                ANNOUNCEMENTS_FILE,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    self.announcements,
                    f,
                    ensure_ascii=False,
                    indent=4
                )
        except Exception as e:
            messagebox.showerror(
                "GREENBIBLE",
                "Could not save announcements:\n" + str(e)
            )


    # EDIT
    def edit_announcement(self):
        selection = self.announcement_list.curselection()

        if not selection:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please select an announcement first."
            )
            return

        index = selection[0]
        original_title = self.announcement_list.get(index)
        original_content = self.announcements.get(
            original_title,
            ""
        )

        editor = tk.Toplevel(self.window)
        editor.title("GREENBIBLE - EDIT ANNOUNCEMENT")
        editor.geometry("900x700")
        editor.minsize(800, 600)
        editor.configure(bg="#151515")
        editor.transient(self.window)
        editor.grab_set()

        # HEADER
        tk.Label(
            editor,
            text="EDIT ANNOUNCEMENT",
            bg="#151515",
            fg="#00ff66",
            font=("Arial", 24, "bold")
        ).pack(
            fill="x",
            pady=12
        )

        # BUTTONS - ALWAYS VISIBLE AT TOP
        button_bar = tk.Frame(
            editor,
            bg="#101010",
            height=70
        )
        button_bar.pack(
            fill="x",
            padx=15,
            pady=8
        )
        button_bar.pack_propagate(False)

        tk.Button(
            button_bar,
            text="SAVE",
            command=lambda: save_changes(),
            bg="#00aa55",
            fg="white",
            activebackground="#00cc66",
            activeforeground="white",
            font=("Arial", 16, "bold"),
            width=15,
            height=2
        ).pack(
            side="left",
            padx=10,
            pady=8
        )

        tk.Button(
            button_bar,
            text="CANCEL",
            command=lambda: cancel_edit(),
            bg="#aa3333",
            fg="white",
            activebackground="#cc4444",
            activeforeground="white",
            font=("Arial", 16, "bold"),
            width=15,
            height=2
        ).pack(
            side="left",
            padx=10,
            pady=8
        )

        # TITLE
        tk.Label(
            editor,
            text="TITLE",
            bg="#151515",
            fg="white",
            font=("Arial", 14, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(8, 3)
        )

        title_entry = tk.Entry(
            editor,
            bg="#252525",
            fg="white",
            insertbackground="white",
            font=("Arial", 17)
        )
        title_entry.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )
        title_entry.insert(
            0,
            original_title
        )

        # CONTENT
        tk.Label(
            editor,
            text="ANNOUNCEMENT CONTENT",
            bg="#151515",
            fg="white",
            font=("Arial", 14, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 3)
        )

        content = tk.Text(
            editor,
            bg="#252525",
            fg="white",
            insertbackground="white",
            font=("Arial", 16),
            wrap="word"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )
        content.insert(
            "1.0",
            original_content
        )

        def save_changes():
            new_title = title_entry.get().strip()
            new_content = content.get(
                "1.0",
                tk.END
            ).strip()

            if not new_title:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter an announcement title.",
                    parent=editor
                )
                return

            if not new_content:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter announcement content.",
                    parent=editor
                )
                return

            if (
                new_title != original_title
                and new_title in self.announcements
            ):
                messagebox.showwarning(
                    "GREENBIBLE",
                    "That announcement title already exists.",
                    parent=editor
                )
                return

            if original_title != new_title:
                self.announcements.pop(
                    original_title,
                    None
                )

            self.announcements[new_title] = new_content

            self.save_announcements()

            self.announcement_list.delete(index)
            self.announcement_list.insert(
                index,
                new_title
            )
            self.announcement_list.selection_set(index)
            self.announcement_list.activate(index)

            self.content.delete(
                "1.0",
                tk.END
            )
            self.content.insert(
                "1.0",
                new_content
            )

            self.current_line = 0

            editor.grab_release()
            editor.destroy()

            messagebox.showinfo(
                "GREENBIBLE",
                "Announcement saved successfully."
            )

        def cancel_edit():
            editor.grab_release()
            editor.destroy()

        title_entry.focus_set()

    # ADD
    def add_announcement(self):
        new_title = simpledialog.askstring(
            "ADD ANNOUNCEMENT",
            "Announcement title:",
            parent=self.window
        )

        if not new_title:
            return

        if new_title in self.announcements:
            messagebox.showwarning(
                "GREENBIBLE",
                "That announcement already exists."
            )
            return

        new_content = simpledialog.askstring(
            "ADD ANNOUNCEMENT",
            "Announcement content:",
            parent=self.window
        )

        if new_content is None:
            return

        self.announcements[new_title] = (
            new_content
        )

        self.save_announcements()

        self.announcement_list.insert(
            tk.END,
            new_title
        )

        messagebox.showinfo(
            "GREENBIBLE",
            "Announcement added successfully."
        )


def open_announcements(parent):
    AnnouncementsWindow(parent)

