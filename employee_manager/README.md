# Employee Data Management System

A desktop application built with **Python + Tkinter + MongoDB** following an **MVC** (Model-View-Controller) architecture.

> Developed by Anand and Payal

---

## Project Structure

```
employee_manager/
├── main.py                        ← Application entry point
├── requirements.txt               ← Python dependencies
├── .env                           ← Environment variables (DB_URL)
├── .gitignore
│
└── app/
    ├── models/
    │   ├── database.py            ← MongoDB connection manager
    │   ├── employee_model.py      ← Employee CRUD & queries
    │   └── user_model.py          ← User auth & password hashing
    │
    ├── controllers/
    │   ├── auth_controller.py     ← Login / Register / Password logic
    │   └── employee_controller.py ← Employee CRUD, search, export, reports
    │
    └── views/
        ├── auth_view.py           ← Welcome, Login, Register, Forgot Password
        ├── dashboard_view.py      ← Sidebar + stat cards navigation
        ├── employee_view.py       ← Employee form + data table (CRUD)
        ├── search_view.py         ← Employee search + detail popup
        ├── export_view.py         ← CSV / PDF export with preview
        ├── reports_view.py        ← Status, Dept, Experience, Age, Gender reports
        └── settings_view.py       ← DB settings, theme, change password
```

---

## Setup & Run

### 1. Clone / download the project

```bash
cd employee_manager
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Edit `.env` and set your MongoDB Atlas connection string:

```
DB_URL=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/
```

### 5. Run the application

```bash
python main.py
```

---

## Features

| Module | Description |
|--------|-------------|
| **Authentication** | Email + bcrypt-hashed password login, registration, forgot password |
| **Employee Management** | Add, update, delete, and view employee records |
| **Search** | Multi-field search with partial/regex matching |
| **Export** | Export to CSV or PDF (all / active / inactive employees) |
| **Reports** | Status, Department, Experience, Age, Gender, Proof-ID distribution |
| **Settings** | DB connection string, theme selector, change password |

---

## Deployment (Windows .exe with PyInstaller)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name EmployeeManager main.py
```

The executable will appear in the `dist/` folder.

> **Note:** Copy your `.env` file next to the generated `.exe` before distributing.
