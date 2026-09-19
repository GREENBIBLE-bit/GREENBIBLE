from pathlib import Path

p = Path("songs.py")
text = p.read_text(encoding="utf-8")

first = text.index("    # =========================\n    # EDIT SONG")
after_first = text.index("    # =========================", first + 30)

# Find the next real section after the duplicate edit_song area.
next_section = text.find("    # =========================", after_first + 30)

if next_section == -1:
    raise RuntimeError("Could not find the next section after EDIT SONG.")

new_block = '''    # =========================
    # EDIT SONG - SLIDE EDITOR
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

        # Convert existing content into slides.
        slides = [
            part.strip()
            for part in original_content.split("---SLIDE---")
            if part.strip()
        ]

        if not slides:
            slides = [""]

        editor = tk.Toplevel(self.window)
        editor.title("GREENBIBLE - SONG EDITOR")
        editor.geometry("1050x750")
        editor.configure(bg="#111111")
        editor.transient(self.window)
        editor.grab_set()

        tk.Label(
            editor,
            text="SONG TITLE",
            fg="white",
            bg="#111111",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))

        title_entry = tk.Entry(
            editor,
            font=("Arial", 16),
            bg="white",
            fg="black"
        )
        title_entry.pack(fill="x", padx=20)
        title_entry.insert(0, original_title)

        main = tk.Frame(editor, bg="#111111")
        main.pack(fill="both", expand=True, padx=20, pady=15)

        left = tk.Frame(main, bg="#222222", width=220)
        left.pack(side="left", fill="y", padx=(0, 15))
        left.pack_propagate(False)

        right = tk.Frame(main, bg="#111111")
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            left,
            text="SONG SLIDES",
            fg="white",
            bg="#222222",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        slide_list = tk.Listbox(
            left,
            font=("Arial", 13),
            bg="white",
            fg="black"
        )
        slide_list.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(
            right,
            text="SLIDE CONTENT / LYRICS",
            fg="white",
            bg="#111111",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        content = tk.Text(
            right,
            font=("Arial", 20),
            bg="white",
            fg="black",
            wrap="word"
        )
        content.pack(fill="both", expand=True, pady=(5, 10))

        current_slide = [0]

        def refresh_slide_list():
            slide_list.delete(0, tk.END)
            for i in range(len(slides)):
                slide_list.insert(tk.END, "Slide " + str(i + 1))

        def load_slide(event=None):
            sel = slide_list.curselection()
            if not sel:
                return

            # Save the slide currently being edited.
            old = current_slide[0]
            if 0 <= old < len(slides):
                slides[old] = content.get("1.0", tk.END).strip()

            current_slide[0] = sel[0]

            content.delete("1.0", tk.END)
            content.insert("1.0", slides[current_slide[0]])

        def add_slide():
            old = current_slide[0]
            if 0 <= old < len(slides):
                slides[old] = content.get("1.0", tk.END).strip()

            slides.append("")
            current_slide[0] = len(slides) - 1

            refresh_slide_list()
            slide_list.selection_clear(0, tk.END)
            slide_list.selection_set(current_slide[0])
            slide_list.activate(current_slide[0])

            content.delete("1.0", tk.END)
            content.focus_set()

        def delete_slide():
            if len(slides) <= 1:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "A song must have at least one slide.",
                    parent=editor
                )
                return

            del slides[current_slide[0]]

            if current_slide[0] >= len(slides):
                current_slide[0] = len(slides) - 1

            refresh_slide_list()
            slide_list.selection_set(current_slide[0])
            slide_list.activate(current_slide[0])

            content.delete("1.0", tk.END)
            content.insert("1.0", slides[current_slide[0]])

        def move_up():
            i = current_slide[0]
            if i <= 0:
                return

            slides[i - 1], slides[i] = slides[i], slides[i - 1]
            current_slide[0] = i - 1

            refresh_slide_list()
            slide_list.selection_set(current_slide[0])
            slide_list.activate(current_slide[0])

        def move_down():
            i = current_slide[0]
            if i >= len(slides) - 1:
                return

            slides[i + 1], slides[i] = slides[i], slides[i + 1]
            current_slide[0] = i + 1

            refresh_slide_list()
            slide_list.selection_set(current_slide[0])
            slide_list.activate(current_slide[0])

        def save_song():
            new_title = title_entry.get().strip()

            if not new_title:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter a song title.",
                    parent=editor
                )
                return

            slides[current_slide[0]] = content.get(
                "1.0",
                tk.END
            ).strip()

            slides[:] = [s.strip() for s in slides if s.strip()]

            if not slides:
                messagebox.showwarning(
                    "GREENBIBLE",
                    "Please enter lyrics for at least one slide.",
                    parent=editor
                )
                return

            new_content = "\\n---SLIDE---\\n".join(slides)

            if original_title != new_title:
                self.songs.pop(original_title, None)

            self.songs[new_title] = new_content

            self.song_list.delete(index)
            self.song_list.insert(index, new_title)
            self.song_list.selection_clear(0, tk.END)
            self.song_list.selection_set(index)
            self.song_list.activate(index)

            if hasattr(self, "save_songs"):
                try:
                    self.save_songs()
                except Exception as e:
                    print("GREENBIBLE SONG SAVE ERROR:", e)

            editor.destroy()

            try:
                self.select_song()
            except Exception:
                pass

            messagebox.showinfo(
                "GREENBIBLE",
                "Song and slides saved successfully.",
                parent=self.window
            )

        slide_list.bind("<<ListboxSelect>>", load_slide)

        buttons = tk.Frame(editor, bg="#111111")
        buttons.pack(fill="x", padx=20, pady=(0, 15))

        tk.Button(
            buttons,
            text="+ ADD SLIDE",
            command=add_slide,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        ).pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="DELETE SLIDE",
            command=delete_slide,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8
        ).pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="MOVE UP",
            command=move_up,
            font=("Arial", 11),
            padx=15,
            pady=8
        ).pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="MOVE DOWN",
            command=move_down,
            font=("Arial", 11),
            padx=15,
            pady=8
        ).pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="SAVE SONG",
            command=save_song,
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side="right", padx=4)

        tk.Button(
            buttons,
            text="CANCEL",
            command=editor.destroy,
            font=("Arial", 11),
            padx=20,
            pady=8
        ).pack(side="right", padx=4)

        refresh_slide_list()
        slide_list.selection_set(0)
        slide_list.activate(0)
        content.insert("1.0", slides[0])


'''

text = text[:first] + new_block + text[next_section:]

p.write_text(text, encoding="utf-8")
print("SONG EDITOR CLEANED AND REBUILT")