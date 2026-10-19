"""
settings_view.py
----------------
Settings view: DB connection string, change password, theme toggle.
"""

import tkinter as tk
from tkinter import RIDGE, StringVar, messagebox
from tkinter import ttk

from app.controllers import auth_controller


class SettingsView:
    """Settings panel embedded inside the Dashboard."""

    # Track the currently logged-in user email so we can change their password
    current_user_email: str = ""

    def __init__(self, parent: tk.Widget):
        self.main_frame = tk.Frame(parent, bg="#82abca")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.main_frame, text="Settings",
            font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50",
        ).pack(pady=20)

        settings_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=RIDGE)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(settings_frame, text="Application Settings", font=("Arial", 16, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        options_frame = tk.Frame(settings_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ── Database section ──────────────────────────────────────────────────
        tk.Label(options_frame, text="Database Settings", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=10, columnspan=2)

        tk.Label(options_frame, text="MongoDB Connection String:", font=("Arial", 12),
                 bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=5)

        import os
        import re
        raw_db_url = os.getenv("DB_URL", "")
        # Mask credentials in UI to prevent exposure during screen sharing/recording
        masked_url = re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1********\3', raw_db_url) if raw_db_url else ""
        self.connection_string = StringVar(value=masked_url)
        conn_entry = tk.Entry(options_frame, textvariable=self.connection_string, font=("Arial", 11),
                              bg="#f0f0f0", width=42, state="readonly")
        conn_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        tk.Label(options_frame, text="(Configured securely in local .env)", font=("Arial", 9, "italic"),
                 bg="white", fg="#7f8c8d").grid(row=1, column=2, sticky="w", padx=5)

        # ── User section ──────────────────────────────────────────────────────
        tk.Label(options_frame, text="User Settings", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50").grid(row=2, column=0, sticky="w", pady=10, columnspan=2)

        tk.Label(options_frame, text="Change Password", font=("Arial", 12),
                 bg="white", fg="#2c3e50").grid(row=3, column=0, sticky="w", pady=5)

        tk.Button(options_frame, text="Change Password", command=self.show_change_password,
                  bg="#3498db", fg="white", font=("Arial", 10)).grid(row=3, column=1, pady=5, padx=5, sticky="w")

        # ── Theme section ─────────────────────────────────────────────────────
        tk.Label(options_frame, text="Application Settings", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50").grid(row=4, column=0, sticky="w", pady=10, columnspan=2)

        tk.Label(options_frame, text="Theme:", font=("Arial", 12),
                 bg="white", fg="#2c3e50").grid(row=5, column=0, sticky="w", pady=5)

        self.theme = StringVar(value="Light")
        theme_combo = ttk.Combobox(options_frame, textvariable=self.theme,
                                   font=("Arial", 12), state="readonly", values=("Light", "Dark"))
        theme_combo.grid(row=5, column=1, pady=5, padx=5, sticky="w")

        tk.Button(settings_frame, text="Save Settings", command=self._save_settings,
                  bg="#2ecc71", fg="white", font=("Arial", 12), width=15).pack(pady=20)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _save_settings(self):
        messagebox.showinfo("Success", "Settings saved successfully.")

    def show_change_password(self):
        win = tk.Toplevel()
        win.title("Change Password")
        win.geometry("400x300")
        win.configure(bg="#f0f0f0")

        frame = tk.Frame(win, bg="#f0f0f0")
        frame.pack(expand=True)

        tk.Label(frame, text="Current Password:", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=10)
        current_pw = tk.Entry(frame, show="*", font=("Arial", 12), width=20)
        current_pw.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(frame, text="New Password:", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10)
        new_pw = tk.Entry(frame, show="*", font=("Arial", 12), width=20)
        new_pw.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(frame, text="Confirm Password:", bg="#f0f0f0", font=("Arial", 12)).grid(row=2, column=0, pady=10, padx=10)
        confirm_pw = tk.Entry(frame, show="*", font=("Arial", 12), width=20)
        confirm_pw.grid(row=2, column=1, pady=10, padx=10)

        def _change():
            success, msg = auth_controller.change_password(
                SettingsView.current_user_email,
                current_pw.get(),
                new_pw.get(),
                confirm_pw.get(),
            )
            if success:
                messagebox.showinfo("Success", msg)
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(frame, text="Change Password", command=_change,
                  bg="#3498db", fg="white", font=("Arial", 12), width=15).grid(row=3, column=0, columnspan=2, pady=20)
