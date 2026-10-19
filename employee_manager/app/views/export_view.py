"""
export_view.py
--------------
Export Data view: format selector, data filter, preview table, export buttons.
"""

import os
import tkinter as tk
from tkinter import BOTH, BOTTOM, HORIZONTAL, RIDGE, RIGHT, VERTICAL, X, Y, StringVar, filedialog, messagebox
from tkinter import ttk

from app.controllers import employee_controller


_PREVIEW_COLS = (
    "emp_id", "name", "designation", "status", "address",
    "email", "contact", "proof_id", "hired_location",
    "doj", "dob", "age", "experience", "gender", "created_at", "updated_at",
)


class ExportView:
    """Export panel embedded inside the Dashboard."""

    def __init__(self, parent: tk.Widget):
        self.main_frame = tk.Frame(parent, bg="#82abca")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.main_frame, text="Export Employee Data",
            font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50",
        ).pack(pady=20)

        self._build_options()
        self._build_preview()

    # ── Options ───────────────────────────────────────────────────────────────

    def _build_options(self):
        export_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=RIDGE)
        export_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=10)

        tk.Label(export_frame, text="Export Options", font=("Arial", 16, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        options_frame = tk.Frame(export_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(options_frame, text="Export Format:", font=("Arial", 12),
                 bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=10)

        self.export_format = StringVar()
        fmt_combo = ttk.Combobox(options_frame, textvariable=self.export_format,
                                 font=("Arial", 12), state="readonly", values=("CSV", "PDF"))
        fmt_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        fmt_combo.current(0)

        tk.Label(options_frame, text="Data to Export:", font=("Arial", 12),
                 bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=10)

        self.export_data_type = StringVar()
        data_combo = ttk.Combobox(
            options_frame, textvariable=self.export_data_type, font=("Arial", 12),
            state="readonly", values=("All Employees", "Active Employees", "Inactive Employees"),
        )
        data_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        data_combo.current(0)

        btn_frame = tk.Frame(options_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Export", command=self._export,
                  bg="#3498db", fg="white", font=("Arial", 12), width=15).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Preview Data", command=self._preview,
                  bg="#2ecc71", fg="white", font=("Arial", 12), width=15).grid(row=0, column=1, padx=10)

    # ── Preview table ─────────────────────────────────────────────────────────

    def _build_preview(self):
        preview_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=RIDGE)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(preview_frame, text="Data Preview", font=("Arial", 16, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        scroll_frame = tk.Frame(preview_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_x = tk.Scrollbar(scroll_frame, orient=HORIZONTAL)
        scroll_y = tk.Scrollbar(scroll_frame, orient=VERTICAL)

        self.preview_table = ttk.Treeview(
            scroll_frame, columns=_PREVIEW_COLS,
            xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set,
        )

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.preview_table.xview)
        scroll_y.config(command=self.preview_table.yview)

        headings = {
            "emp_id": "EMP ID", "name": "Name", "designation": "Designation",
            "status": "Status", "address": "Address", "email": "Email",
            "contact": "Contact", "proof_id": "Proof ID", "hired_location": "Hired Location",
            "doj": "Date of Joining", "dob": "Date of Birth", "age": "Age",
            "experience": "Experience", "gender": "Gender",
            "created_at": "Created At", "updated_at": "Updated At",
        }
        widths = {
            "emp_id": 100, "name": 150, "designation": 150, "status": 100, "address": 200,
            "email": 200, "contact": 150, "proof_id": 150, "hired_location": 150,
            "doj": 150, "dob": 150, "age": 100, "experience": 100, "gender": 100,
            "created_at": 150, "updated_at": 150,
        }
        for col in _PREVIEW_COLS:
            self.preview_table.heading(col, text=headings[col])
            self.preview_table.column(col, width=widths[col])

        self.preview_table["show"] = "headings"
        self.preview_table.pack(fill=BOTH, expand=True)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _preview(self):
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)
        data = employee_controller.get_export_data(self.export_data_type.get())
        for rec in data:
            self.preview_table.insert("", "end", values=(
                rec.get("emp_id", ""), rec.get("name", ""), rec.get("designation", ""),
                rec.get("status", ""), rec.get("address", ""), rec.get("email", ""),
                rec.get("contact", ""), rec.get("proof_id", ""), rec.get("hired_location", ""),
                rec.get("doj", ""), rec.get("dob", ""), rec.get("age", ""),
                rec.get("experience", ""), rec.get("gender", ""),
                rec.get("created_at", ""), rec.get("updated_at", ""),
            ))

    def _export(self):
        fmt = self.export_format.get()
        data_type = self.export_data_type.get()
        data = employee_controller.get_export_data(data_type)

        if not data:
            messagebox.showinfo("Info", "No data to export.")
            return

        if fmt == "CSV":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{data_type.replace(' ', '_')}.csv",
            )
            if not file_path:
                return
            success, msg = employee_controller.export_to_csv(data, file_path)
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"{data_type.replace(' ', '_')}.pdf",
            )
            if not file_path:
                return
            success, msg = employee_controller.export_to_pdf(data, data_type, file_path)

        if success:
            messagebox.showinfo("Success", msg)
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
        else:
            messagebox.showerror("Error", msg)
