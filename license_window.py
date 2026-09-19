import tkinter as tk
from tkinter import messagebox

from license_manager import (
    activate_license,
    deactivate_license,
    get_license_status,
)


def show_license_window(parent):
    win = tk.Toplevel(parent)
    win.title("GREENBIBLE — License & Activation")
    win.geometry("560x430")
    win.resizable(False, False)

    try:
        win.transient(parent)
    except Exception:
        pass

    title = tk.Label(
        win,
        text="GREENBIBLE",
        font=("Arial", 24, "bold")
    )
    title.pack(pady=(22, 2))

    subtitle = tk.Label(
        win,
        text="License & Activation",
        font=("Arial", 13)
    )
    subtitle.pack(pady=(0, 18))

    status_frame = tk.LabelFrame(
        win,
        text=" Current License Status ",
        padx=18,
        pady=15
    )
    status_frame.pack(fill="x", padx=25, pady=5)

    status_label = tk.Label(
        status_frame,
        text="",
        font=("Arial", 12, "bold"),
        justify="left",
        anchor="w"
    )
    status_label.pack(fill="x")

    form = tk.Frame(win)
    form.pack(fill="x", padx=45, pady=18)

    tk.Label(
        form,
        text="License Key:"
    ).grid(row=0, column=0, sticky="w", pady=7)

    key_entry = tk.Entry(
        form,
        width=42,
        font=("Arial", 11)
    )
    key_entry.grid(row=0, column=1, padx=10, pady=7)

    tk.Label(
        form,
        text="Customer Email:"
    ).grid(row=1, column=0, sticky="w", pady=7)

    email_entry = tk.Entry(
        form,
        width=42,
        font=("Arial", 11)
    )
    email_entry.grid(row=1, column=1, padx=10, pady=7)

    def refresh_status():
        status = get_license_status()

        if status.get("licensed"):
            text = (
                "STATUS: ACTIVE\n"
                f"Customer: {status.get('customer_email', '')}\n"
                f"License Key: {status.get('license_key', '')}"
            )
        else:
            text = (
                "STATUS: TRIAL\n"
                f"Days Remaining: {status.get('days_left', 0)}\n"
                f"{status.get('message', '')}"
            )

        status_label.config(text=text)

    def do_activate():
        key = key_entry.get().strip()
        email = email_entry.get().strip()

        if not key:
            messagebox.showwarning(
                "GREENBIBLE",
                "Please enter your license key.",
                parent=win
            )
            return

        result = activate_license(key, email)

        if result.get("success"):
            messagebox.showinfo(
                "GREENBIBLE",
                result.get("message", "GREENBIBLE activated."),
                parent=win
            )
            refresh_status()
        else:
            messagebox.showerror(
                "Activation Failed",
                result.get("message", "Activation failed."),
                parent=win
            )

    def do_deactivate():
        answer = messagebox.askyesno(
            "Deactivate GREENBIBLE",
            "Do you want to deactivate the current GREENBIBLE license?",
            parent=win
        )

        if not answer:
            return

        result = deactivate_license()

        if result.get("success"):
            messagebox.showinfo(
                "GREENBIBLE",
                result.get("message", "License deactivated."),
                parent=win
            )
            refresh_status()
        else:
            messagebox.showerror(
                "GREENBIBLE",
                result.get("message", "Unable to deactivate license."),
                parent=win
            )

    buttons = tk.Frame(win)
    buttons.pack(pady=8)

    tk.Button(
        buttons,
        text="ACTIVATE GREENBIBLE",
        width=22,
        command=do_activate
    ).pack(side="left", padx=6)

    tk.Button(
        buttons,
        text="DEACTIVATE",
        width=14,
        command=do_deactivate
    ).pack(side="left", padx=6)

    tk.Button(
        buttons,
        text="CLOSE",
        width=12,
        command=win.destroy
    ).pack(side="left", padx=6)

    refresh_status()

    return win