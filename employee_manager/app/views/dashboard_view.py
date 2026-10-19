"""
dashboard_view.py
-----------------
Dashboard view: sidebar navigation + stat cards + content area.
Hosts all embedded sub-views (Employee, Search, Export, Reports, Settings).
"""

import tkinter as tk
from tkinter import messagebox

from app.controllers import employee_controller


class DashboardView:
    """Main application dashboard shown after a successful login."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.dashboard = tk.Toplevel(root)
        self.dashboard.title("Employee Management Dashboard")
        self.dashboard.geometry("1350x700+0+0")
        self.dashboard.configure(bg="#2c3e50")

        self._build_sidebar()
        self._build_content_area()
        self._show_welcome()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = tk.Frame(self.dashboard, bg="#2c3e50", width=200, height=700)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Home", font=("Arial", 20, "bold"),
                 bg="#2c3e50", fg="white", pady=50).pack(fill=tk.X)

        # Back-to-welcome button
        tk.Button(sidebar, text="← Back to Login", command=self.dashboard.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12),
                  bd=0, pady=10, width=20).pack(fill=tk.X, pady=5, side=tk.TOP)

        nav_btns = [
            ("Employee Management", self._open_employee),
            ("Search Employee",     self._open_search),
            ("Export Data",         self._open_export),
            ("Reports",             self._open_reports),
            ("Settings",            self._open_settings),
        ]
        for text, cmd in nav_btns:
            tk.Button(sidebar, text=text, command=cmd,
                      bg="#34495e", fg="white", font=("Arial", 12),
                      bd=0, pady=10, width=20).pack(fill=tk.X, pady=20)

        tk.Button(sidebar, text="Logout", command=self.dashboard.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12),
                  bd=0, pady=10, width=20).pack(fill=tk.X, pady=5, side=tk.BOTTOM)

    # ── Content area ──────────────────────────────────────────────────────────

    def _build_content_area(self):
        self.content_frame = tk.Frame(self.dashboard, bg="#ecf0f1")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _clear_content(self):
        """Destroy all children in the content area (not the sidebar)."""
        for widget in self.dashboard.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()

    # ── Welcome screen ────────────────────────────────────────────────────────

    def _show_welcome(self):
        self._clear_content()

        content = tk.Frame(self.dashboard, bg="#ecf0f1")
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(content, text="Welcome to the Employee Management Dashboard",
                 font=("Arial", 24, "bold"), bg="#ecf0f1", fg="#2c3e50", pady=20).pack(pady=30)

        # ── Stat boxes ────────────────────────────────────────────────────────
        stats_frame = tk.Frame(content, bg="#ecf0f1")
        stats_frame.pack(pady=20)

        try:
            stats = employee_controller.get_dashboard_stats()
        except Exception:
            stats = {"total": "N/A", "active": "N/A", "inactive": "N/A", "new_this_month": "N/A"}

        self._stat_box(stats_frame, "Total Employees",    str(stats["total"]),          "#3498db", 0, 0)
        self._stat_box(stats_frame, "Active Employees",   str(stats["active"]),          "#2ecc71", 0, 1)
        self._stat_box(stats_frame, "Inactive Employees", str(stats["inactive"]),        "#e74c3c", 1, 0)
        self._stat_box(stats_frame, "New This Month",     str(stats["new_this_month"]), "#f39c12", 1, 1)

    @staticmethod
    def _stat_box(parent, title, value, color, row, col):
        box = tk.Frame(parent, bg=color, width=200, height=100, padx=20, pady=20)
        box.grid(row=row, column=col, padx=10, pady=10)
        box.grid_propagate(False)
        tk.Label(box, text=title, font=("Arial", 12), bg=color, fg="white").pack(anchor="w")
        tk.Label(box, text=value, font=("Arial", 24, "bold"), bg=color, fg="white").pack(anchor="center", pady=10)

    # ── Navigation handlers ───────────────────────────────────────────────────

    def _open_employee(self):
        self._clear_content()
        from app.views.employee_view import EmployeeView
        EmployeeView(self.dashboard)

    def _open_search(self):
        self._clear_content()
        from app.views.search_view import SearchView
        SearchView(self.dashboard)

    def _open_export(self):
        self._clear_content()
        from app.views.export_view import ExportView
        ExportView(self.dashboard)

    def _open_reports(self):
        self._clear_content()
        from app.views.reports_view import ReportsView
        ReportsView(self.dashboard)

    def _open_settings(self):
        self._clear_content()
        from app.views.settings_view import SettingsView
        SettingsView(self.dashboard)
