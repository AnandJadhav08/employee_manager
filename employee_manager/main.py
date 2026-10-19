"""
main.py
-------
Application entry point.
Run with:  python main.py
"""

import tkinter as tk
from app.views.auth_view import AuthView


def main():
    root = tk.Tk()
    AuthView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
