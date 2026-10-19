"""
employee_controller.py
----------------------
Business-logic layer for employee management (CRUD, search, export, reports).
Sits between the employee views and the employee model.
"""

import csv
import datetime
import os
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from app.models import employee_model


# ── CRUD ──────────────────────────────────────────────────────────────────────

def save_employee(data: dict) -> tuple[bool, str]:
    """Save a new employee. Returns (success, message)."""
    emp_id = data.get("emp_id", "").strip()
    if not emp_id:
        return False, "Employee ID is required."
    if employee_model.employee_exists(emp_id):
        return False, "Employee ID already exists."
    try:
        employee_model.insert_employee(data)
        return True, "Record saved successfully!"
    except Exception as exc:
        return False, f"Error: {exc}"


def update_employee(emp_id: str, data: dict) -> tuple[bool, str]:
    """Update an existing employee. Returns (success, message)."""
    if not emp_id:
        return False, "Employee ID is required."
    try:
        employee_model.update_employee(emp_id, data)
        return True, "Record updated successfully!"
    except Exception as exc:
        return False, f"Error: {exc}"


def delete_employee(emp_id: str) -> tuple[bool, str]:
    """Delete an employee. Returns (success, message)."""
    if not emp_id:
        return False, "Employee ID is required."
    try:
        employee_model.delete_employee(emp_id)
        return True, "Record deleted successfully!"
    except Exception as exc:
        return False, f"Error: {exc}"


# ── SEARCH ────────────────────────────────────────────────────────────────────

def search_employees(search_by: str, search_text: str) -> tuple[list[dict], str]:
    """
    Search employees.
    Returns (records: list, error_message: str).
    error_message is empty on success.
    """
    if not search_text:
        return [], "Please enter search text."
    records = employee_model.search_employees(search_by, search_text)
    if not records:
        return [], "No matching records found."
    return records, ""


def get_all_employees() -> list[dict]:
    return employee_model.get_all_employees()


# ── DASHBOARD STATS ───────────────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    return {
        "total": employee_model.count_employees(),
        "active": employee_model.count_employees({"status": "Active"}),
        "inactive": employee_model.count_employees({"status": "Inactive"}),
        "new_this_month": employee_model.count_employees(
            {
                "created_at": {
                    "$gte": datetime.datetime.now().replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                }
            }
        ),
    }


# ── EXPORT ────────────────────────────────────────────────────────────────────

_EXPORT_FIELDS = [
    "emp_id", "name", "designation", "age", "gender",
    "experience", "email", "contact", "hired_location",
    "status", "address", "proof_id", "dob", "doj",
    "created_at", "updated_at",
]


def _get_export_query(export_data_type: str) -> dict:
    if export_data_type == "Active Employees":
        return {"status": "Active"}
    if export_data_type == "Inactive Employees":
        return {"status": "Inactive"}
    return {}


def get_export_data(export_data_type: str) -> list[dict]:
    return employee_model.get_employees_by_query(_get_export_query(export_data_type))


def export_to_csv(data: list[dict], file_path: str) -> tuple[bool, str]:
    """Export employee data to CSV. Returns (success, message)."""
    try:
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=_EXPORT_FIELDS, extrasaction="ignore")
            writer.writeheader()
            for record in data:
                # Remove MongoDB internal fields
                row = {k: v for k, v in record.items() if k in _EXPORT_FIELDS}
                writer.writerow(row)
        return True, f"Data exported successfully to {file_path}"
    except Exception as exc:
        return False, f"Error exporting data: {exc}"


def export_to_pdf(data: list[dict], export_data_type: str, file_path: str) -> tuple[bool, str]:
    """Export employee data to PDF. Returns (success, message)."""
    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(f"Employee Data - {export_data_type}", styles["Title"]),
            Paragraph(" ", styles["Normal"]),
        ]

        table_data = [["Emp ID", "Name", "Designation", "Status", "Email", "DOB", "Experience", "Gender"]]
        for record in data:
            table_data.append([
                record.get("emp_id", ""),
                record.get("name", ""),
                record.get("designation", ""),
                record.get("status", ""),
                record.get("email", ""),
                record.get("dob", ""),
                record.get("experience", ""),
                record.get("gender", ""),
            ])

        table = Table(table_data)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ])
        )
        elements.append(table)
        elements.append(Paragraph(" ", styles["Normal"]))
        elements.append(
            Paragraph(
                f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        doc.build(elements)
        return True, f"Data exported successfully to {file_path}"
    except Exception as exc:
        return False, f"Error exporting data: {exc}"


# ── REPORTS ───────────────────────────────────────────────────────────────────

def get_status_report() -> dict:
    """Return counts for Active / Inactive / On Leave employees."""
    return {
        "Active": employee_model.count_employees({"status": "Active"}),
        "Inactive": employee_model.count_employees({"status": "Inactive"}),
        "On Leave": employee_model.count_employees({"status": "On Leave"}),
    }


def get_department_report() -> list[dict]:
    """Return aggregated employee counts per designation."""
    pipeline = [
        {"$group": {"_id": "$designation", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return employee_model.aggregate_employees(pipeline)


def get_gender_report() -> dict:
    """Return aggregated employee counts per gender."""
    pipeline = [
        {"$group": {"_id": "$gender", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    rows = employee_model.aggregate_employees(pipeline)
    return {r["_id"] or "Not Specified": r["count"] for r in rows}


def get_age_report() -> dict:
    """Return employee counts bucketed by age ranges."""
    employees = employee_model.get_all_employees()
    buckets = {"Under 25": 0, "25–35": 0, "36–45": 0, "46–55": 0, "55+": 0, "Not specified": 0}
    for emp in employees:
        try:
            age = float(str(emp.get("age", "")).strip())
            if age < 25:
                buckets["Under 25"] += 1
            elif age < 36:
                buckets["25–35"] += 1
            elif age < 46:
                buckets["36–45"] += 1
            elif age < 56:
                buckets["46–55"] += 1
            else:
                buckets["55+"] += 1
        except ValueError:
            buckets["Not specified"] += 1
    return buckets


def _categorize_experience(exp_value) -> str:
    exp_str = str(exp_value).strip().lower()
    if not exp_str:
        return "Not specified"
    try:
        years = float(exp_str)
    except ValueError:
        m = re.search(r"(\d+\.?\d*)", exp_str)
        if m:
            years = float(m.group(1))
        else:
            return "Not specified"
    if years < 1:
        return "Less than 1 year"
    if years < 3:
        return "1–3 years"
    if years < 5:
        return "3–5 years"
    if years < 10:
        return "5–10 years"
    return "10+ years"


def get_experience_report() -> tuple[dict, dict]:
    """
    Returns (categories: dict[str, int], categorized_employees: dict[str, list]).
    """
    order = ["Less than 1 year", "1–3 years", "3–5 years", "5–10 years", "10+ years", "Not specified"]
    categories = {k: 0 for k in order}
    categorized = {k: [] for k in order}

    employees = employee_model.get_employees_by_query({})

    for emp in employees:
        cat = _categorize_experience(emp.get("experience", ""))
        categories[cat] += 1
        categorized[cat].append(emp)

    return categories, categorized


def get_proof_id_report() -> dict:
    """Return employee counts bucketed by proof ID type (Aadhar / PAN / Passport / Other)."""
    employees = employee_model.get_all_employees()
    buckets: dict[str, int] = {}
    for emp in employees:
        pid = str(emp.get("proof_id", "Not specified") or "Not specified")
        # Classify by keyword
        key = "Not specified"
        pl = pid.lower()
        if "aadhar" in pl or "aadhaar" in pl:
            key = "Aadhar"
        elif "pan" in pl:
            key = "PAN"
        elif "passport" in pl:
            key = "Passport"
        elif pid != "Not specified":
            key = "Other"
        buckets[key] = buckets.get(key, 0) + 1
    return buckets


# ── STATUS REPORT PDF EXPORT ──────────────────────────────────────────────────

def export_status_report_pdf(
    active: int, inactive: int, on_leave: int, file_path: str
) -> tuple[bool, str]:
    try:
        total = active + inactive + on_leave
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Employee Status Distribution Report", styles["Title"]),
            Paragraph(" ", styles["Normal"]),
        ]
        table_data = [["Status", "Count", "Percentage"]]
        for label, count in [("Active", active), ("Inactive", inactive), ("On Leave", on_leave)]:
            pct = f"{(count / total) * 100:.2f}%" if total else "0.00%"
            table_data.append([label, str(count), pct])
        table_data.append(["Total", str(total), "100.00%"])

        table = Table(table_data)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ])
        )
        elements.append(table)
        elements.append(Paragraph(" ", styles["Normal"]))
        elements.append(
            Paragraph(
                f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        doc.build(elements)
        return True, f"Report exported successfully to {file_path}"
    except Exception as exc:
        return False, f"Error exporting report: {exc}"


def export_department_report_pdf(department_data: list[dict], file_path: str) -> tuple[bool, str]:
    try:
        total = sum(d["count"] for d in department_data)
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Employee Department Distribution Report", styles["Title"]),
            Paragraph(" ", styles["Normal"]),
        ]
        table_data = [["Department/Designation", "Count", "Percentage"]]
        for dept in department_data:
            name = dept["_id"] or "Not Specified"
            pct = f"{(dept['count'] / total) * 100:.2f}%" if total else "0.00%"
            table_data.append([name, str(dept["count"]), pct])
        table_data.append(["Total", str(total), "100.00%"])

        table = Table(table_data)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ])
        )
        elements.append(table)
        elements.append(Paragraph(" ", styles["Normal"]))
        elements.append(
            Paragraph(
                f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        doc.build(elements)
        return True, f"Report exported successfully to {file_path}"
    except Exception as exc:
        return False, f"Error exporting report: {exc}"
