"""
auth_view.py
------------
Authentication views: Welcome screen, Login, Register, Forgot Password.
All UI code for the authentication flow lives here.
"""

import re
import tkinter as tk
from tkinter import messagebox

from app.controllers import auth_controller


class AuthView:
    """Root welcome window with Admin and Register buttons."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Employee Data Management System | Developed by Anand and Payal")
        self.root.geometry("1350x700+0+0")
        self.root.configure(bg="#cacaca")

        # ── Top-right button frame ────────────────────────────────────────────
        btn_frame = tk.Frame(root, bg="#cacaca")
        btn_frame.pack(anchor="ne", padx=10, pady=10)

        tk.Button(
            btn_frame, text="Admin", command=self.show_login_window,
            bg="#4CAF50", fg="white", font=("Arial", 10), width=10, height=1,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="Register", command=self.show_register_window,
            bg="#2196F3", fg="white", font=("Arial", 10), width=10, height=1,
        ).pack(side=tk.LEFT)

        # ── Welcome text ──────────────────────────────────────────────────────
        welcome_frame = tk.Frame(root, bg="#cacaca")
        welcome_frame.pack(expand=True)

        tk.Label(
            welcome_frame,
            text="Welcome to Our Employee Data Management System",
            font=("Helvetica", 40, "bold"),
            fg="#0d4f70", bg="#cacaca",
        ).pack(pady=10)

        tk.Label(
            welcome_frame,
            text="Your Gateway to Seamless Authentication",
            font=("Georgia", 18, "italic"),
            fg="dark green", bg="#cacaca",
        ).pack(pady=5)

        tk.Label(
            welcome_frame,
            text="✦ ━━━━━━━━━━━━━━━ ✦",
            font=("Arial", 16),
            fg="#000000", bg="#cacaca",
        ).pack(pady=20)

    # ── Login ─────────────────────────────────────────────────────────────────

    def show_login_window(self):
        win = tk.Toplevel(self.root)
        win.title("Admin Login")
        win.geometry("1350x700+0+0")
        win.configure(bg="#cacaca")

        tk.Button(
            win, text="←", command=win.destroy,
            font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0,
        ).place(x=5, y=5)

        frame = tk.Frame(win, bg="#f0f0f0")
        frame.pack(expand=True)

        tk.Label(frame, text="Email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=20, padx=20)
        email_entry = tk.Entry(frame, font=("Arial", 14), width=25)
        email_entry.grid(row=0, column=1, pady=20, padx=20)

        tk.Label(frame, text="Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=1, column=0, pady=20, padx=20)
        password_entry = tk.Entry(frame, show="*", font=("Arial", 14), width=25)
        password_entry.grid(row=1, column=1, pady=20, padx=20)

        tk.Label(
            frame,
            text="Password must be at least 6 characters with numbers and symbols",
            bg="#f0f0f0", font=("Arial", 10), fg="#666666",
        ).grid(row=2, column=0, columnspan=2, pady=5)

        def _login():
            success, msg = auth_controller.login(email_entry.get(), password_entry.get())
            if success:
                messagebox.showinfo("Success", msg)
                win.destroy()
                # Import here to avoid circular deps
                from app.views.dashboard_view import DashboardView
                DashboardView(self.root)
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            frame, text="Login", command=_login,
            bg="#4CAF50", fg="white", font=("Arial", 14), width=20,
        ).grid(row=3, column=0, columnspan=2, pady=20)

        forgot_lbl = tk.Label(
            frame, text="Forgot Password?", bg="#f0f0f0",
            font=("Arial", 10, "underline"), fg="#0000FF", cursor="hand2",
        )
        forgot_lbl.grid(row=4, column=0, columnspan=2)
        forgot_lbl.bind("<Button-1>", lambda e: self.show_forgot_password_window())

    # ── Register ──────────────────────────────────────────────────────────────

    def show_register_window(self):
        win = tk.Toplevel(self.root)
        win.title("Register")
        win.geometry("1350x700+0+0")
        win.configure(bg="#cacaca")

        tk.Button(
            win, text="←", command=win.destroy,
            font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0,
        ).place(x=5, y=5)

        frame = tk.Frame(win, bg="#f0f0f0")
        frame.pack(expand=True)

        tk.Label(frame, text="Full Name:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=15, padx=20)
        full_name_entry = tk.Entry(frame, font=("Arial", 14), width=25)
        full_name_entry.grid(row=0, column=1, pady=15, padx=20)

        tk.Label(frame, text="Email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=1, column=0, pady=15, padx=20)
        email_entry = tk.Entry(frame, font=("Arial", 14), width=25)
        email_entry.grid(row=1, column=1, pady=15, padx=20)

        tk.Label(frame, text="Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=2, column=0, pady=15, padx=20)
        password_entry = tk.Entry(frame, show="*", font=("Arial", 14), width=25)
        password_entry.grid(row=2, column=1, pady=15, padx=20)

        tk.Label(frame, text="Confirm Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=3, column=0, pady=15, padx=20)
        confirm_entry = tk.Entry(frame, show="*", font=("Arial", 14), width=25)
        confirm_entry.grid(row=3, column=1, pady=15, padx=20)

        tk.Label(
            frame,
            text="Password must be at least 6 characters with numbers and symbols",
            bg="#f0f0f0", font=("Arial", 10), fg="#666666",
        ).grid(row=4, column=0, columnspan=2, pady=5)

        def _register():
            success, msg = auth_controller.register(
                full_name_entry.get(),
                email_entry.get(),
                password_entry.get(),
                confirm_entry.get(),
            )
            if success:
                messagebox.showinfo("Success", msg)
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            frame, text="Register", command=_register,
            bg="#2196F3", fg="white", font=("Arial", 14), width=20,
        ).grid(row=5, column=0, columnspan=2, pady=20)

    # ── Forgot Password ───────────────────────────────────────────────────────

    def show_forgot_password_window(self):
        win = tk.Toplevel(self.root)
        win.title("Forgot Password")
        win.geometry("450x250")
        win.configure(bg="#f0f0f0")

        tk.Button(
            win, text="←", command=win.destroy,
            font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0,
        ).place(x=5, y=5)

        frame = tk.Frame(win, bg="#f0f0f0")
        frame.pack(expand=True)

        tk.Label(frame, text="Enter your registered email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=20, padx=20)
        email_entry = tk.Entry(frame, font=("Arial", 14), width=25)
        email_entry.grid(row=0, column=1, pady=20, padx=20)

        def _reset():
            success, msg = auth_controller.request_password_reset(email_entry.get())
            if success:
                messagebox.showinfo("Success", msg)
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            frame, text="Reset Password", command=_reset,
            bg="#FF9800", fg="white", font=("Arial", 14), width=15,
        ).grid(row=1, column=0, columnspan=2, pady=20)
