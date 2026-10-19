"""
reports_view.py
---------------
Reports view: report cards + individual report windows (Status, Department,
Experience, Age, Gender, Proof-ID, Salary placeholder, Location placeholder).
"""

import os
import tkinter as tk
from tkinter import BOTH, HORIZONTAL, RIDGE, RIGHT, VERTICAL, X, Y, StringVar, filedialog, messagebox
from tkinter import ttk

from app.controllers import employee_controller


class ReportsView:
    """Reports panel embedded inside the Dashboard."""

    def __init__(self, parent: tk.Widget):
        self.main_frame = tk.Frame(parent, bg="#82abca")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.main_frame, text="Employee Reports",
            font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50",
        ).pack(pady=20)

        self._build_report_cards()

    # ── Report cards grid ─────────────────────────────────────────────────────

    def _build_report_cards(self):
        grid = tk.Frame(self.main_frame, bg="#ecf0f1")
        grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        cards = [
            ("Employee Status Report",   "View distribution of employees by status",         self.show_status_report,     0, 0),
            ("Department Distribution",  "View employees by department/designation",           self.show_department_report, 0, 1),
            ("Experience Analysis",      "View employee experience distribution",              self.show_experience_report, 1, 0),
            ("Location Distribution",    "View employees by hired location",                   self._coming_soon,           1, 1),
            ("Age Analysis",             "View employee age distribution",                     self.show_age_report,        2, 0),
            ("Gender Distribution",      "View employee gender distribution",                  self.show_gender_report,     2, 1),
            ("Salary Analysis",          "View employee salary distribution",                  self._coming_soon,           3, 0),
            ("Proof ID Distribution",    "View employee proof ID distribution",                self.show_proof_id_report,   3, 1),
        ]

        for title, desc, cmd, row, col in cards:
            self._create_card(grid, title, desc, cmd, row, col)

    def _create_card(self, parent, title, description, command, row, col):
        card = tk.Frame(parent, bg="white", bd=1, relief=RIDGE, width=300, height=200)
        card.grid(row=row, column=col, padx=20, pady=20)
        card.grid_propagate(False)

        tk.Label(card, text=title, font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        tk.Label(card, text=description, font=("Arial", 10),
                 bg="white", fg="#7f8c8d", wraplength=250).pack(fill=tk.X, padx=10)
        tk.Button(card, text="View Report", command=command,
                  bg="#3498db", fg="white", font=("Arial", 10)).pack(pady=20)

    def _coming_soon(self):
        messagebox.showinfo("Coming Soon", "This report is under development.")

    # ── Status Report ─────────────────────────────────────────────────────────

    def show_status_report(self):
        data = employee_controller.get_status_report()
        total = sum(data.values())

        win = tk.Toplevel()
        win.title("Employee Status Report")
        win.geometry("600x500")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee Status Distribution",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)

        frame = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        colors_map = {"Active": "#2ecc71", "Inactive": "#e74c3c", "On Leave": "#f39c12"}
        for status, count in data.items():
            tk.Label(frame, text=f"{status}: {count}", font=("Arial", 14),
                     bg="white", fg=colors_map.get(status, "#2c3e50"), pady=10).pack(fill=tk.X, padx=20)

        tk.Label(frame, text=f"Total Employees: {total}", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X, padx=20)

        tk.Button(win, text="Export Report",
                  command=lambda: self._export_status_pdf(data["Active"], data["Inactive"], data["On Leave"]),
                  bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)

    def _export_status_pdf(self, active, inactive, on_leave):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
            initialfile="Employee_Status_Report.pdf",
        )
        if not file_path:
            return
        success, msg = employee_controller.export_status_report_pdf(active, inactive, on_leave, file_path)
        if success:
            messagebox.showinfo("Success", msg)
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
        else:
            messagebox.showerror("Error", msg)

    # ── Department Report ─────────────────────────────────────────────────────

    def show_department_report(self):
        dept_data = employee_controller.get_department_report()
        total = sum(d["count"] for d in dept_data)

        win = tk.Toplevel()
        win.title("Department Distribution Report")
        win.geometry("600x500")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee Department Distribution",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)

        frame = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scroll_frame = tk.Frame(frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_y = tk.Scrollbar(scroll_frame, orient=VERTICAL)
        dept_table = ttk.Treeview(scroll_frame, columns=("department", "count"),
                                  yscrollcommand=scroll_y.set)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=dept_table.yview)

        dept_table.heading("department", text="Department/Designation")
        dept_table.heading("count", text="Number of Employees")
        dept_table.column("department", width=300)
        dept_table.column("count", width=200)
        dept_table["show"] = "headings"
        dept_table.pack(fill=BOTH, expand=True)

        for dept in dept_data:
            dept_table.insert("", "end", values=(dept["_id"] or "Not Specified", dept["count"]))

        tk.Label(win, text=f"Total Employees: {total}", font=("Arial", 12, "bold"),
                 bg="#f0f0f0", fg="#2c3e50").pack(pady=5)

        tk.Button(win, text="Export Report",
                  command=lambda: self._export_dept_pdf(dept_data),
                  bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)

    def _export_dept_pdf(self, dept_data):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
            initialfile="Department_Distribution_Report.pdf",
        )
        if not file_path:
            return
        success, msg = employee_controller.export_department_report_pdf(dept_data, file_path)
        if success:
            messagebox.showinfo("Success", msg)
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
        else:
            messagebox.showerror("Error", msg)

    # ── Experience Report ─────────────────────────────────────────────────────

    def show_experience_report(self):
        try:
            categories, categorized = employee_controller.get_experience_report()
            total_employees = sum(categories.values())
        except Exception as exc:
            messagebox.showerror("Error", f"Error generating report: {exc}")
            return

        win = tk.Toplevel()
        win.title("Experience Profile Analytics")
        win.geometry("700x500")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee Experience Distribution Analysis",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)

        main_container = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left_panel = tk.Frame(main_container, bg="white", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(main_container, bg="white")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── Summary table (left) ──────────────────────────────────────────────
        tk.Label(left_panel, text="Experience Summary", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=5)

        summary_frame = tk.Frame(left_panel, bg="white")
        summary_frame.pack(fill=tk.X, pady=5)

        for lbl, col in [("Experience Range", 0), ("Count", 1), ("Percentage", 2)]:
            tk.Label(summary_frame, text=lbl, font=("Arial", 11, "bold"),
                     bg="#3498db", fg="white").grid(row=0, column=col, sticky="ew", padx=1, pady=1)

        for idx, (cat, count) in enumerate(categories.items(), 1):
            bg = "#f9f9f9" if idx % 2 == 0 else "white"
            pct = f"{(count / total_employees) * 100:.2f}%" if total_employees else "0.00%"
            tk.Label(summary_frame, text=cat, font=("Arial", 10), bg=bg).grid(row=idx, column=0, sticky="w", padx=5, pady=1)
            tk.Label(summary_frame, text=str(count), font=("Arial", 10), bg=bg).grid(row=idx, column=1, padx=5, pady=1)
            tk.Label(summary_frame, text=pct, font=("Arial", 10), bg=bg).grid(row=idx, column=2, padx=5, pady=1)

        total_row = len(categories) + 1
        for col, val in enumerate(["Total", str(total_employees), "100.00%"]):
            tk.Label(summary_frame, text=val, font=("Arial", 10, "bold"),
                     bg="#ecf0f1").grid(row=total_row, column=col, padx=5, pady=1, sticky="w" if col == 0 else "")

        # ── Employee list (right) ─────────────────────────────────────────────
        tk.Label(right_panel, text="Employee List", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=5)

        tk.Label(right_panel, text="Select Experience Range:", font=("Arial", 11), bg="white").pack(anchor="w", padx=5)

        selected_range = StringVar()
        range_dd = ttk.Combobox(right_panel, textvariable=selected_range,
                                values=list(categories.keys()), state="readonly", width=30)
        range_dd.pack(anchor="w", padx=5, pady=5)
        range_dd.current(0)

        count_var = StringVar(value=f"Employees: {categories[list(categories.keys())[0]]}")
        tk.Label(right_panel, textvariable=count_var, font=("Arial", 11, "bold"),
                 bg="white", fg="#2c3e50").pack(anchor="w", padx=5, pady=5)

        list_frame = tk.Frame(right_panel, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scroll_y = tk.Scrollbar(list_frame, orient=VERTICAL)
        emp_list = tk.Listbox(list_frame, font=("Arial", 11), height=15, yscrollcommand=scroll_y.set)
        scroll_y.config(command=emp_list.yview)
        scroll_y.pack(side=RIGHT, fill=Y)
        emp_list.pack(fill=BOTH, expand=True)

        def _update_list(*_):
            emp_list.delete(0, tk.END)
            sel = selected_range.get()
            emps = categorized.get(sel, [])
            count_var.set(f"Employees: {len(emps)}")
            if not emps:
                emp_list.insert(tk.END, "No employees in this category")
            else:
                for emp in emps:
                    emp_list.insert(tk.END,
                                    f"{emp.get('name', 'Unknown')} - {emp.get('designation', 'Unknown')} - {emp.get('experience', 'N/A')}")

        selected_range.trace("w", _update_list)
        _update_list()

    # ── Age Report ────────────────────────────────────────────────────────────

    def show_age_report(self):
        data = employee_controller.get_age_report()
        total = sum(data.values())

        win = tk.Toplevel()
        win.title("Age Distribution Report")
        win.geometry("500x400")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee Age Distribution",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)

        frame = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for bucket, count in data.items():
            pct = f"{(count / total) * 100:.1f}%" if total else "0.0%"
            tk.Label(frame, text=f"{bucket}: {count}  ({pct})",
                     font=("Arial", 13), bg="white", fg="#2c3e50", pady=8, anchor="w").pack(fill=tk.X, padx=20)

        tk.Label(frame, text=f"Total: {total}", font=("Arial", 13, "bold"),
                 bg="white", fg="#2c3e50", pady=8, anchor="w").pack(fill=tk.X, padx=20)

    # ── Gender Report ─────────────────────────────────────────────────────────

    def show_gender_report(self):
        data = employee_controller.get_gender_report()
        total = sum(data.values())

        win = tk.Toplevel()
        win.title("Gender Distribution Report")
        win.geometry("450x350")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee Gender Distribution",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)

        frame = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for gender, count in data.items():
            pct = f"{(count / total) * 100:.1f}%" if total else "0.0%"
            tk.Label(frame, text=f"{gender}: {count}  ({pct})",
                     font=("Arial", 13), bg="white", fg="#2c3e50", pady=8, anchor="w").pack(fill=tk.X, padx=20)

        tk.Label(frame, text=f"Total: {total}", font=("Arial", 13, "bold"),
                 bg="white", fg="#2c3e50", pady=8, anchor="w").pack(fill=tk.X, padx=20)

    # ── Proof-ID Report ───────────────────────────────────────────────────────

    def show_proof_id_report(self):
        data = employee_controller.get_proof_id_report()
        total = sum(data.values())

        win = tk.Toplevel()
        win.title("Proof ID Distribution Report")
        win.geometry("450x350")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee Proof ID Distribution",
                 font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)

        frame = tk.Frame(win, bg="white", bd=2, relief=RIDGE)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for pid_type, count in data.items():
            pct = f"{(count / total) * 100:.1f}%" if total else "0.0%"
            tk.Label(frame, text=f"{pid_type}: {count}  ({pct})",
                     font=("Arial", 13), bg="white", fg="#2c3e50", pady=8, anchor="w").pack(fill=tk.X, padx=20)

        tk.Label(frame, text=f"Total: {total}", font=("Arial", 13, "bold"),
                 bg="white", fg="#2c3e50", pady=8, anchor="w").pack(fill=tk.X, padx=20)
