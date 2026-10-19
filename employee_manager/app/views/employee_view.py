"""
employee_view.py
----------------
Employee Management view: form + data table + CRUD actions.
"""

import tkinter as tk
from tkinter import BOTH, BOTTOM, HORIZONTAL, RIDGE, RIGHT, VERTICAL, X, Y, StringVar, messagebox
from tkinter import ttk

from app.controllers import employee_controller


class EmployeeView:
    """Employee management panel embedded inside the Dashboard."""

    def __init__(self, parent: tk.Widget):
        # ── Main frame ────────────────────────────────────────────────────────
        self.main_frame = tk.Frame(parent, bg="#82abca")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.main_frame, text="Employee Management",
            font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50",
        ).pack(pady=20)

        content_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self._build_form(content_frame)
        self._build_table(content_frame)
        self.fetch_data()

    # ── Form ──────────────────────────────────────────────────────────────────

    def _build_form(self, parent: tk.Widget):
        form_frame = tk.Frame(parent, bg="white", bd=2, relief=RIDGE)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            form_frame, text="Employee Details",
            font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10,
        ).pack(fill=tk.X)

        # ── StringVars ───────────────────────────────────────────────────────
        self.var_emp_id        = StringVar()
        self.var_designation   = StringVar()
        self.var_name          = StringVar()
        self.var_dob           = StringVar()
        self.var_doj           = StringVar()
        self.var_age           = StringVar()
        self.var_experience    = StringVar()
        self.var_gender        = StringVar()
        self.var_proof_id      = StringVar()
        self.var_email         = StringVar()
        self.var_contact       = StringVar()
        self.var_hired_location = StringVar()
        self.var_status        = StringVar()
        self.var_address       = StringVar()
        self.var_created_at    = StringVar()
        self.var_updated_at    = StringVar()

        fields_frame = tk.Frame(form_frame, bg="white")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        def lbl(text, row, col, **kw):
            tk.Label(fields_frame, text=text, font=("Arial", 12), bg="white", fg="#2c3e50", **kw).grid(
                row=row, column=col, sticky="w", pady=5
            )

        def entry(var, row, col, width=None, **kw):
            cfg = {"textvariable": var, "font": ("Arial", 12), "bg": "#f0f0f0"}
            if width:
                cfg["width"] = width
            tk.Entry(fields_frame, **cfg, **kw).grid(row=row, column=col, pady=5, padx=5, sticky="w")

        lbl("Employee ID",   0, 0); entry(self.var_emp_id,       0, 1)
        lbl("Name",          1, 0); entry(self.var_name,          1, 1)
        lbl("Designation",   1, 2, padx=10); entry(self.var_designation, 1, 3)
        lbl("DOB",           2, 0); entry(self.var_dob,           2, 1)
        lbl("DOJ",           2, 2, padx=10); entry(self.var_doj,  2, 3)
        lbl("Age",           3, 0); entry(self.var_age,           3, 1)
        lbl("Gender",        3, 2, padx=10)
        gender_combo = ttk.Combobox(
            fields_frame, textvariable=self.var_gender,
            font=("Arial", 12), state="readonly", values=("Male", "Female", "Other"),
        )
        gender_combo.grid(row=3, column=3, pady=5, padx=5, sticky="w")
        gender_combo.current(0)

        lbl("Experience",    4, 0); entry(self.var_experience,   4, 1)
        lbl("Proof ID",      4, 2, padx=10); entry(self.var_proof_id,    4, 3)
        lbl("Email",         5, 0); entry(self.var_email,         5, 1)
        lbl("Contact",       5, 2, padx=10); entry(self.var_contact,      5, 3)
        lbl("Hired Location",6, 0); entry(self.var_hired_location,6, 1)
        lbl("Status",        6, 2, padx=10)
        status_combo = ttk.Combobox(
            fields_frame, textvariable=self.var_status,
            font=("Arial", 12), state="readonly", values=("Active", "Inactive", "On Leave"),
        )
        status_combo.grid(row=6, column=3, pady=5, padx=5, sticky="w")
        status_combo.current(0)

        lbl("Address",       7, 0)
        tk.Entry(
            fields_frame, textvariable=self.var_address, font=("Arial", 12),
            bg="#f0f0f0", width=50,
        ).grid(row=7, column=1, columnspan=3, pady=5, padx=5, sticky="w")

        # ── CRUD buttons ──────────────────────────────────────────────────────
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)

        for col, (text, cmd, color) in enumerate([
            ("Save",   self.save_data,   "#2ecc71"),
            ("Update", self.update_data, "#3498db"),
            ("Delete", self.delete_data, "#e74c3c"),
            ("Clear",  self.clear_data,  "#95a5a6"),
        ]):
            tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="white",
                      font=("Arial", 12), width=10).grid(row=0, column=col, padx=5)

    # ── Table ─────────────────────────────────────────────────────────────────

    def _build_table(self, parent: tk.Widget):
        table_frame = tk.Frame(parent, bg="white", bd=2, relief=RIDGE)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            table_frame, text="Employee Records",
            font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10,
        ).pack(fill=tk.X)

        scroll_frame = tk.Frame(table_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_x = tk.Scrollbar(scroll_frame, orient=HORIZONTAL)
        scroll_y = tk.Scrollbar(scroll_frame, orient=VERTICAL)

        _COLS = (
            "emp_id", "name", "designation", "age", "gender",
            "experience", "email", "contact", "hired_location",
            "status", "address", "proof_id", "created_at", "updated_at", "doj", "dob",
        )
        self.employee_table = ttk.Treeview(
            scroll_frame, columns=_COLS,
            xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set,
        )

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.employee_table.xview)
        scroll_y.config(command=self.employee_table.yview)

        headings = {
            "emp_id": "EMP ID", "name": "Name", "designation": "Designation",
            "age": "Age", "gender": "Gender", "experience": "Experience",
            "email": "Email", "contact": "Contact", "hired_location": "Hired Location",
            "status": "Status", "address": "Address", "proof_id": "Proof ID",
            "created_at": "Created At", "updated_at": "Updated At", "doj": "DOJ", "dob": "DOB",
        }
        widths = {
            "emp_id": 100, "name": 150, "designation": 150, "age": 50, "gender": 80,
            "experience": 100, "email": 150, "contact": 100, "hired_location": 150,
            "status": 100, "address": 200, "proof_id": 150, "created_at": 150,
            "updated_at": 150, "doj": 100, "dob": 100,
        }
        for col in _COLS:
            self.employee_table.heading(col, text=headings[col])
            self.employee_table.column(col, width=widths[col])

        self.employee_table["show"] = "headings"
        self.employee_table.pack(fill=BOTH, expand=True)
        self.employee_table.bind("<ButtonRelease-1>", self._on_row_select)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def fetch_data(self):
        for item in self.employee_table.get_children():
            self.employee_table.delete(item)
        for rec in employee_controller.get_all_employees():
            self.employee_table.insert("", "end", values=(
                rec.get("emp_id", ""), rec.get("name", ""), rec.get("designation", ""),
                rec.get("age", ""), rec.get("gender", ""), rec.get("experience", ""),
                rec.get("email", ""), rec.get("contact", ""), rec.get("hired_location", ""),
                rec.get("status", ""), rec.get("address", ""), rec.get("proof_id", ""),
                rec.get("created_at", ""), rec.get("updated_at", ""),
                rec.get("doj", ""), rec.get("dob", ""),
            ))

    def _on_row_select(self, _event):
        selected = self.employee_table.focus()
        data = self.employee_table.item(selected, "values")
        if not data:
            return
        from app.models import employee_model
        emp = employee_model.get_employee_by_id(data[0])
        if emp:
            self.var_emp_id.set(emp.get("emp_id", ""))
            self.var_name.set(emp.get("name", ""))
            self.var_designation.set(emp.get("designation", ""))
            self.var_dob.set(emp.get("dob", ""))
            self.var_doj.set(emp.get("doj", ""))
            self.var_age.set(emp.get("age", ""))
            self.var_experience.set(emp.get("experience", ""))
            self.var_gender.set(emp.get("gender", ""))
            self.var_proof_id.set(emp.get("proof_id", ""))
            self.var_email.set(emp.get("email", ""))
            self.var_contact.set(emp.get("contact", ""))
            self.var_hired_location.set(emp.get("hired_location", ""))
            self.var_status.set(emp.get("status", ""))
            self.var_address.set(emp.get("address", ""))
            self.var_created_at.set(emp.get("created_at", ""))
            self.var_updated_at.set(emp.get("updated_at", ""))

    def _collect_form_data(self) -> dict:
        return {
            "emp_id":          self.var_emp_id.get(),
            "designation":     self.var_designation.get(),
            "name":            self.var_name.get(),
            "dob":             self.var_dob.get(),
            "doj":             self.var_doj.get(),
            "age":             self.var_age.get(),
            "experience":      self.var_experience.get(),
            "gender":          self.var_gender.get(),
            "proof_id":        self.var_proof_id.get(),
            "email":           self.var_email.get(),
            "contact":         self.var_contact.get(),
            "hired_location":  self.var_hired_location.get(),
            "status":          self.var_status.get(),
            "address":         self.var_address.get(),
        }

    # ── CRUD actions ──────────────────────────────────────────────────────────

    def save_data(self):
        data = self._collect_form_data()
        success, msg = employee_controller.save_employee(data)
        if success:
            messagebox.showinfo("Success", msg)
            self.fetch_data()
        else:
            messagebox.showerror("Error", msg)

    def update_data(self):
        emp_id = self.var_emp_id.get()
        data = self._collect_form_data()
        data.pop("emp_id", None)  # don't overwrite the ID field
        success, msg = employee_controller.update_employee(emp_id, data)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_data()
            self.fetch_data()
        else:
            messagebox.showerror("Error", msg)

    def delete_data(self):
        emp_id = self.var_emp_id.get()
        if not emp_id:
            messagebox.showerror("Error", "Employee ID is required.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            success, msg = employee_controller.delete_employee(emp_id)
            if success:
                messagebox.showinfo("Success", msg)
                self.clear_data()
                self.fetch_data()
            else:
                messagebox.showerror("Error", msg)

    def clear_data(self):
        for var in (
            self.var_emp_id, self.var_designation, self.var_name,
            self.var_dob, self.var_doj, self.var_age, self.var_experience,
            self.var_gender, self.var_proof_id, self.var_email, self.var_contact,
            self.var_hired_location, self.var_status, self.var_address,
            self.var_created_at, self.var_updated_at,
        ):
            var.set("")
