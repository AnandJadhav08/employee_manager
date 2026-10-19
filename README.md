# 🚀 Employee Management System (Python + Tkinter + MongoDB)

A desktop-based **Employee Management System** built with **Python**, **Tkinter**, and **MongoDB Atlas**, organized following the **MVC (Model-View-Controller)** pattern with built-in security practices.

> **Authors:** Anand and Payal  
> **Repository:** [AnandJadhav08/employee_manager](https://github.com/AnandJadhav08/employee_manager)

---

## 🔒 Security Best Practices & Design

This project adheres to strict security standards to ensure credentials and data are protected:

1. **Zero Secret Exposure in Version Control:**
   - Real connection strings, passwords, and API keys are **never** committed to Git.
   - `.env` is strictly ignored by `.gitignore`.
   - `.env.example` is provided as a sanitized template.

2. **Secure Password Storage:**
   - User credentials in the database are hashed with **`bcrypt`** using unique, randomized salts (`gensalt()`).
   - Passwords are never stored, logged, or retrieved in plain text.

3. **In-App Credential Masking:**
   - Database connection strings displayed in the Settings UI are masked (e.g. `mongodb+srv://<user>:********@cluster...`) to prevent credential leakage during screen sharing or demos.

4. **Principle of Least Privilege:**
   - Database user roles in MongoDB Atlas should be limited to application databases (`user_auth_db`, `employee_management`).

---

## 📁 Project Structure

```text
.
├── README.md                   # Single central documentation file
└── employee_manager/
    ├── main.py                 # Application entry point (MVC)
    ├── requirements.txt        # Python dependencies
    ├── .env.example            # Sanitized template for environment variables
    ├── .env                    # Local secret config (DB_URL - NEVER commit)
    ├── .gitignore              # Gitignore rules for secrets, venv, and caches
    ├── SECURITY_REPORT.md      # Security audit and verification report
    │
    ├── app/                    # MVC Application Package
    │   ├── models/             # Database connection & models
    │   │   ├── database.py     # MongoDB connection loader (reads DB_URL from .env)
    │   │   ├── employee_model.py # Employee CRUD operations & aggregation
    │   │   └── user_model.py   # User authentication & bcrypt hashing
    │   │
    │   ├── controllers/        # Business logic
    │   │   ├── auth_controller.py     # Authentication & password strength validation
    │   │   └── employee_controller.py # Employee business logic, search, export & reports
    │   │
    │   └── views/              # UI Components (Tkinter)
    │       ├── auth_view.py    # Welcome, Login, Register, Forgot Password
    │       ├── dashboard_view.py # Main dashboard with sidebar & statistics
    │       ├── employee_view.py # Employee form & data table (CRUD)
    │       ├── search_view.py  # Search dialogue
    │       ├── export_view.py  # CSV / PDF export preview
    │       ├── reports_view.py # Analytics & distribution reports
    │       └── settings_view.py # Masked DB connection info & themes
    │
    └── new_emp_manage.py       # Legacy single-file version (reference)
```

---

## ⚙️ How to Setup and Run

### 1. Prerequisites
- **Python 3.10 to 3.13** installed on your system.
- A **MongoDB Atlas** account (or local MongoDB server).

---

### 2. Navigate to the Project

Open your terminal in the project directory:

```bash
cd employee_manager
```

---

### 3. Create & Activate Virtual Environment

Keep dependencies isolated to prevent system conflicts:

**Windows (PowerShell / Command Prompt):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

*Note: If PowerShell displays a script restriction error, run:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 4. Install Dependencies

Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Packages installed:
- `pymongo>=4.6.0` (MongoDB driver)
- `bcrypt>=4.0.1` (Password hashing)
- `pandas>=2.0.0` (Data processing & reports)
- `reportlab>=4.0.0` (PDF generation)
- `python-dotenv>=1.0.0` (Environment variable management)

---

### 5. Configure Secrets (`.env`)

> ⚠️ **CRITICAL SECURITY RULE:** Never put real passwords in `main.py`, `.env.example`, or any tracked file. Always use a local `.env`.

1. **Create your `.env` file from `.env.example`:**
   - **Windows:**
     ```cmd
     copy .env.example .env
     ```
   - **macOS / Linux:**
     ```bash
     cp .env.example .env
     ```

2. **Configure your MongoDB Atlas Connection String:**
   - In MongoDB Atlas, go to **Database Access** and create a database user with password.
   - Under **Network Access**, add your current IP address (or `0.0.0.0/0` for initial testing).
   - Under **Clusters > Connect > Drivers > Python**, copy the connection string.
   - Open `.env` and fill in your connection string:
     ```env
     DB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
     ```
     *(Replace `<username>` and `<password>` with your database user credentials. If your password contains special characters like `@` or `:`, URL-encode them).*

---

### 6. Run the Application

Launch the application using:

```bash
python main.py
```

---

## 🧭 First-Time Usage Guide

1. **Register Admin:**
   - On the Welcome screen, click **Register**.
   - Enter your email and a strong password (minimum 6 characters, must include at least 1 number and 1 special character).
   - Click **Submit**. Your password is salted and hashed with `bcrypt` before storage.
2. **Log In:**
   - Click **Admin** on the welcome screen.
   - Enter your registered email and password to access the Dashboard.
3. **Use Modules:**
   - **Employee Menu:** Add, update, delete, and view employee records.
   - **Search:** Search across multiple fields.
   - **Export:** Export data to CSV or generate PDF salary bills.
   - **Reports:** View department, status, age, and experience analytics.
   - **Settings:** Check masked DB connection and toggle themes.

---

## 🛡️ Pre-Push Security Checklist

Before running `git commit` or `git push`:

- [ ] Run `git status` — ensure `.env` is **NOT** listed.
- [ ] Run `git diff` — confirm no passwords, connection strings, or personal secrets are present in any modified files.
- [ ] Verify that only `.env.example` (with dummy placeholders) is committed.

---

## ❓ Common Troubleshooting

| Issue | Cause & Solution |
|---|---|
| `ValueError: DB_URL is not set` | Missing `.env` file in `employee_manager/`. Copy `.env.example` to `.env` and define `DB_URL`. |
| `ServerSelectionTimeoutError` | MongoDB Atlas IP access issue. Check **Network Access** in Atlas to whitelist your current IP address. |
| `Authentication failed` | Incorrect MongoDB user or password in `DB_URL`. Special characters in passwords must be URL-encoded. |
| `No module named '_tkinter'` (Linux) | Install Tkinter on Linux via `sudo apt-get install python3-tk`. |
