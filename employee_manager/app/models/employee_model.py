"""
employee_model.py
-----------------
Data-access layer for employee records (CRUD + queries).
All MongoDB interactions for the employees collection live here.
"""

import datetime
from app.models.database import get_employees_collection


def _col():
    return get_employees_collection()


# ── CREATE ────────────────────────────────────────────────────────────────────

def insert_employee(data: dict) -> bool:
    """Insert a new employee document. Returns True on success."""
    data["created_at"] = datetime.datetime.now()
    _col().insert_one(data)
    return True


# ── READ ──────────────────────────────────────────────────────────────────────

def employee_exists(emp_id: str) -> bool:
    return _col().find_one({"emp_id": emp_id}) is not None


def get_employee_by_id(emp_id: str) -> dict | None:
    return _col().find_one({"emp_id": emp_id})


def get_all_employees() -> list[dict]:
    return list(_col().find())


def get_employees_by_query(query: dict) -> list[dict]:
    return list(_col().find(query))


def count_employees(query: dict = {}) -> int:
    return _col().count_documents(query)


def aggregate_employees(pipeline: list) -> list[dict]:
    return list(_col().aggregate(pipeline))


# ── UPDATE ────────────────────────────────────────────────────────────────────

def update_employee(emp_id: str, data: dict) -> bool:
    """Update an existing employee's fields. Returns True on success."""
    data["updated_at"] = datetime.datetime.now()
    result = _col().update_one({"emp_id": emp_id}, {"$set": data})
    return result.modified_count > 0


# ── DELETE ────────────────────────────────────────────────────────────────────

def delete_employee(emp_id: str) -> bool:
    """Delete an employee by emp_id. Returns True on success."""
    result = _col().delete_one({"emp_id": emp_id})
    return result.deleted_count > 0


# ── SEARCH ────────────────────────────────────────────────────────────────────

# Maps human-readable column names to MongoDB field names
FIELD_MAP = {
    "Employee ID": "emp_id",
    "Name": "name",
    "Designation": "designation",
    "Hired Location": "hired_location",
    "Proof ID": "proof_id",
    "Address": "address",
    "DOB": "dob",
    "DOJ": "doj",
    "Status": "status",
    "Email": "email",
    "Contact": "contact",
    "Age": "age",
    "Experience": "experience",
    "Gender": "gender",
    "Created At": "created_at",
    "Updated At": "updated_at",
}


def search_employees(search_by: str, search_text: str) -> list[dict]:
    """Return employees matching a partial (case-insensitive) search."""
    field = FIELD_MAP.get(search_by)
    if not field:
        return []
    query = {field: {"$regex": search_text, "$options": "i"}}
    return list(_col().find(query))
