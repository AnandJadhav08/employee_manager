"""
search_view.py
--------------
Search Employee view: search form + results table + detail popup.
"""

import tkinter as tk
from tkinter import BOTH, BOTTOM, HORIZONTAL, RIDGE, RIGHT, VERTICAL, X, Y, StringVar, messagebox
from tkinter import ttk

from app.controllers import employee_controller
from app.models.employee_model import FIELD_MAP


_SEARCH_OPTIONS = list(FIELD_MAP.keys())

_RESULT_COLS = (
    "emp_id", "name", "designation", "age", "gender",
    "experience", "email", "contact", "status",
    "created_at", "updated_at", "hired_location",
    "proof_id", "address", "dob", "doj",
)


class SearchView:
    """Search employee panel embedded inside the Dashboard."""

    def __init__(self, parent: tk.Widget):
        self.main_frame = tk.Frame(parent, bg="#82abca")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.main_frame, text="Search Employee Records",
            font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50",
        ).pack(pady=20)

        self._build_search_bar()
        self._build_results_table()
        self._load_all()

    # ── Search bar ────────────────────────────────────────────────────────────

    def _build_search_bar(self):
        search_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=RIDGE)
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(search_frame, text="Search By:", font=("Arial", 12),
                 bg="white", fg="#2c3e50", pady=10, padx=10).grid(row=0, column=0)

        self.search_by = StringVar()
        combo = ttk.Combobox(search_frame, textvariable=self.search_by,
                             font=("Arial", 12), state="readonly", values=_SEARCH_OPTIONS)
        combo.grid(row=0, column=1, padx=10, pady=10)
        combo.current(0)

        self.search_text = StringVar()
        tk.Entry(search_frame, textvariable=self.search_text,
                 font=("Arial", 12), bg="#f0f0f0", width=30).grid(row=0, column=2, padx=10, pady=10)

        tk.Button(search_frame, text="Search", command=self._search,
                  bg="#3498db", fg="white", font=("Arial", 12), width=10).grid(row=0, column=3, padx=10, pady=10)

        tk.Button(search_frame, text="Show All", command=self._load_all,
                  bg="#2ecc71", fg="white", font=("Arial", 12), width=10).grid(row=0, column=4, padx=10, pady=10)

    # ── Results table ─────────────────────────────────────────────────────────

    def _build_results_table(self):
        results_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=RIDGE)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(results_frame, text="Search Results", font=("Arial", 16, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        scroll_frame = tk.Frame(results_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_x = tk.Scrollbar(scroll_frame, orient=HORIZONTAL)
        scroll_y = tk.Scrollbar(scroll_frame, orient=VERTICAL)

        self.search_table = ttk.Treeview(
            scroll_frame, columns=_RESULT_COLS,
            xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set,
        )

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.search_table.xview)
        scroll_y.config(command=self.search_table.yview)

        headings = {
            "emp_id": "EMP ID", "name": "Name", "designation": "Designation",
            "age": "Age", "gender": "Gender", "experience": "Experience",
            "email": "Email", "contact": "Contact", "status": "Status",
            "created_at": "Created At", "updated_at": "Updated At",
            "hired_location": "Hired Location", "proof_id": "Proof ID",
            "address": "Address", "dob": "DOB", "doj": "DOJ",
        }
        widths = {
            "emp_id": 100, "name": 150, "designation": 150, "age": 50,
            "gender": 80, "experience": 100, "email": 150, "contact": 100,
            "status": 100, "created_at": 150, "updated_at": 150,
            "hired_location": 150, "proof_id": 100, "address": 150, "dob": 100, "doj": 100,
        }
        for col in _RESULT_COLS:
            self.search_table.heading(col, text=headings[col])
            self.search_table.column(col, width=widths[col])

        self.search_table["show"] = "headings"
        self.search_table.pack(fill=BOTH, expand=True)
        self.search_table.bind("<Double-1>", self._view_full_details)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _populate_table(self, records: list[dict]):
        for item in self.search_table.get_children():
            self.search_table.delete(item)
        for rec in records:
            self.search_table.insert("", "end", values=(
                rec.get("emp_id", ""), rec.get("name", ""), rec.get("designation", ""),
                rec.get("age", ""), rec.get("gender", ""), rec.get("experience", ""),
                rec.get("email", ""), rec.get("contact", ""), rec.get("status", ""),
                rec.get("created_at", ""), rec.get("updated_at", ""),
                rec.get("hired_location", ""), rec.get("proof_id", ""),
                rec.get("address", ""), rec.get("dob", ""), rec.get("doj", ""),
            ))

    def _search(self):
        records, err = employee_controller.search_employees(
            self.search_by.get(), self.search_text.get()
        )
        self._populate_table(records)
        if err:
            messagebox.showinfo("Info", err)

    def _load_all(self):
        self._populate_table(employee_controller.get_all_employees())

    def _view_full_details(self, _event):
        selected = self.search_table.focus()
        data = self.search_table.item(selected, "values")
        if not data:
            return
        from app.models import employee_model
        emp = employee_model.get_employee_by_id(data[0])
        if not emp:
            return

        win = tk.Toplevel()
        win.title(f"Employee Details – {data[1]}")
        win.geometry("600x500")
        win.configure(bg="#f0f0f0")

        details_frame = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            details_frame, text=f"Details for {emp.get('name', '')}",
            font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10,
        ).pack(fill=tk.X)

        info_frame = tk.Frame(details_frame, bg="white")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for row_idx, (key, value) in enumerate(emp.items()):
            if key not in ["_id", "created_at", "updated_at"]:
                tk.Label(
                    info_frame,
                    text=key.replace("_", " ").title() + ":",
                    font=("Arial", 12, "bold"), bg="white", fg="#2c3e50", anchor="w",
                ).grid(row=row_idx, column=0, sticky="w", pady=5)
                tk.Label(
                    info_frame, text=str(value),
                    font=("Arial", 12), bg="white", fg="#34495e", anchor="w",
                ).grid(row=row_idx, column=1, sticky="w", pady=5, padx=10)

        tk.Button(win, text="Close", command=win.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12), width=10).pack(pady=10)
