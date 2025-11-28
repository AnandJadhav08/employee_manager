# 🚀 Employee Management System (Python + Tkinter + MongoDB Atlas)

A desktop-based **Employee Management System** built using **Python Tkinter**, **MongoDB Atlas**, and **ReportLab**.  
This application allows administrators to manage employee data, generate salary bills, export reports, and enforce secure authentication with bcrypt hashing.

---

## 📌 Problem Statement

Organizations often struggle with:

- Managing employee records: storing, updating, and deleting data.
- Tracking salary/payment details.
- Generating bills or salary slips.
- Maintaining secure user authentication.
- Using outdated or manual systems like Excel sheets.
- Lack of a centralized cloud-backed database to prevent data loss.

There is a need for a **simple, secure, desktop-based system** that manages all employee information in one place.

---

## ✅ Solution: This Employee Management System

This application solves these issues with:

- A clean, functional **Tkinter UI**
- **MongoDB Atlas** for secure cloud data storage
- **bcrypt hashing** for password security
- **ReportLab-generated PDF bills**
- Full CRUD operations (Create, Read, Update, Delete)
- Employee salary management
- Dashboard to view all employees in a Treeview table

---

## ✨ Features

### 🔐 Authentication System
- Register new admin users  
- Login securely (password hashed with bcrypt)  
- Password confirmation and validation  
- Forgot password placeholder  

### 👨‍💼 Employee Management
- Add new employees  
- Update employee details  
- Delete employees  
- View employees in an interactive table  
- Auto-fill details when selecting a table row  

### 💰 Salary & Billing
- Generate salary bills  
- Auto-generated Record IDs  
- PDF bills using ReportLab  

### 📜 Data Storage
- Uses **MongoDB Atlas**  
- Collections:  
  - `login_app` (users)  
  - `Employee_table` (employee records)  

---

# 🛠️ Tech Stack

### Frontend / UI
- Python Tkinter  
- ttkbootstrap (optional)  

### Backend
- Python 3.10+  
- MongoDB Atlas  
- bcrypt  

### PDF Generation
- ReportLab  

### Libraries
- pymongo  
- pillow  
- datetime  
- tkinter.ttk  

# 📁 Project Structure

```
employee_manager/
│
├── .gitignore             
├── Requirement.txt   # Dependencies Document                (Optional Requirement.txt)
├── README.md           # Project documentation
└── new_emp_manage.py.  # # Main Tkinter + MongoDB application
```

---

# ⚙️ Setup & Installation (Using uv)

This project uses **uv**, a fast Python environment + package manager.

---

## 1️⃣ Install uv

```sh
pip install uv
```

---

## 2️⃣ Create virtual environment

```sh
uv venv
```

---

## 3️⃣ Activate environment

### Windows
```sh
.\.venv\Scriptsctivate
```

### macOS / Linux
```sh
source .venv/bin/activate
```

---

## 4️⃣ Install dependencies

```sh
uv pip install -r requirements.txt
```

If needed, create `requirements.txt`:

```
pymongo
reportlab
pillow
bcrypt
ttkbootstrap
```

---

## 5️⃣ Run the Application

```sh
uv run app.py
```

---

# 🗄️ MongoDB Atlas Setup

## 1️⃣ Create a Free Atlas Account  
https://www.mongodb.com/cloud/atlas

## 2️⃣ Create a Cluster (Free M0)

## 3️⃣ Add Database User  
- **Username:** python_user  
- **Password:** yourPassword  
- **Role:** Read/Write Any Database  

## 4️⃣ Add IP Address  
Allow access from anywhere:

```
0.0.0.0/0
```

## 5️⃣ Get the Connection String

Example:

```
mongodb+srv://<username>:<password>@cluster0.mongodb.net/
```

## 6️⃣ Add to Your Code

```python
client = pymongo.MongoClient(
    "mongodb+srv://python_user:yourPassword@cluster0.mongodb.net/")
```

---

# 📦 Environment Variables (Recommended)

Create `.env`:

```
MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
```

Load it using:

```python
from dotenv import load_dotenv
load_dotenv()
import os

MONGO_URI = os.getenv("MONGO_URI")
```

---

# ▶️ How to Use the Application

1. Run the program  
2. Register an admin (first launch)  
3. Login  
4. Go to Employee menu  
5. Add/Update/Delete employees  
6. Generate PDF salary bills  
7. View employees in the dashboard table  

---

# 📌 Future Improvements

- Light/Dark themes  
- Export to Excel/CSV  
- Search & Filter employees  
- Attendance module  
- QR-based salary slips  
- Multi-role accounts (Admin/HR/Finance)  

