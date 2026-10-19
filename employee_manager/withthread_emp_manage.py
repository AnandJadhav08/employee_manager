# new_emp_manage.py
# Requires: python >=3.8 (your comment mentioned 3.13 — fine)
import re
import threading
import os
import csv
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Scrollbar, HORIZONTAL, VERTICAL, RIGHT, BOTTOM, X, Y, BOTH
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Load .env
load_dotenv()
db_url = os.getenv("DB_URL") or os.getenv("db_url")  # support both names

# Connect to MongoDB (use a short timeout so connection problems surface quickly)
try:
    client = MongoClient(db_url, serverSelectionTimeoutMS=5000)
    # Optionally verify connection (this may raise if unreachable)
    client.server_info()
except Exception as e:
    # We'll allow app to continue but show an error if DB actions fail
    print("Warning: MongoDB connection failed at startup:", e)
    client = None

class AuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Data Management System | Developed by Anand and Payal")
        self.root.geometry("1350x700+0+0")
        self.root.configure(bg="#cacaca")

        # Keep references for DB collections (set later if client available)
        self.client = client
        if self.client:
            self.db = self.client['employee_management']
            self.users_collection = self.client['user_auth_db']['Email_users']
        else:
            self.db = None
            self.users_collection = None
        # --- Top Button Frame ---
        button_frame = tk.Frame(root, bg="#cacaca")
        button_frame.pack(anchor='ne', padx=10, pady=10)
        tk.Button(button_frame, text="Admin", command=self.show_login_frame,
                  bg="#4CAF50", fg="white", font=("Arial", 10), width=10, height=1).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Register", command=self.show_register_frame,
                  bg="#2196F3", fg="white", font=("Arial", 10), width=10, height=1).pack(side=tk.LEFT)

        # Welcome Frame
        welcome_frame = tk.Frame(root, bg="#cacaca")
        welcome_frame.pack(expand=True)
        tk.Label(welcome_frame,
                 text="Welcome to Our Employee Data Management System",
                 font=("Helvetica", 40, "bold"),
                 fg="#0d4f70",
                 bg="#cacaca").pack(pady=10)
        tk.Label(welcome_frame,
                 text="Your Gateway to Seamless Authentication",
                 font=("Georgia", 18, "italic"),
                 fg="dark green",
                 bg="#cacaca").pack(pady=5)
        tk.Label(welcome_frame,
                 text="✦ ━━━━━━━━━━━━━━━ ✦",
                 font=("Arial", 16),
                 fg="#000000",
                 bg="#cacaca").pack(pady=20)

    # ----------------------- Login / Register / Forgot -----------------------
    def show_login_frame(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Admin Login")
        login_window.geometry("500x350")
        login_window.configure(bg="#cacaca")
        back_btn = tk.Button(login_window, text="←", command=login_window.destroy,
                             font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        frame = tk.Frame(login_window, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)

        tk.Label(frame, text="Email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=10, padx=10)
        email = tk.Entry(frame, font=("Arial", 14), width=30)
        email.grid(row=0, column=1, pady=10, padx=10)
        tk.Label(frame, text="Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=1, column=0, pady=10, padx=10)
        password = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
        password.grid(row=1, column=1, pady=10, padx=10)

        def login_action():
            user_email = email.get().strip()
            user_password = password.get().strip()
            if not user_email or not user_password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, user_email):
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            # DB access (may be slow) - do quickly and then continue (light query)
            try:
                if self.client is None:
                    raise Exception("DB client not available")
                user = self.client['user_auth_db']['Email_users'].find_one({"email": user_email})
            except Exception as e:
                messagebox.showerror("Error", f"DB error: {e}")
                return
            if user and bcrypt.checkpw(user_password.encode('utf-8'), user['password']):
                # Update last login
                try:
                    self.client['user_auth_db']['Email_users'].update_one({"email": user_email}, {"$set": {"last_login": datetime.datetime.now()}})
                except Exception:
                    pass
                messagebox.showinfo("Success", "Login Successful!")
                login_window.destroy()
                # show dashboard in main thread
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid Email or Password")

        tk.Button(frame, text="Login", command=login_action,
                  bg="#4CAF50", fg="white", font=("Arial", 14), width=20).grid(row=3, column=0, columnspan=2, pady=20)
        forgot_password = tk.Label(frame, text="Forgot Password?", bg="#f0f0f0",
                                   font=("Arial", 10, "underline"), fg="#0000FF", cursor="hand2")
        forgot_password.grid(row=4, column=0, columnspan=2)
        forgot_password.bind("<Button-1>", lambda e: self.show_forgot_password())

    def show_register_frame(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("600x450")
        register_window.configure(bg="#cacaca")
        back_btn = tk.Button(register_window, text="←", command=register_window.destroy,
                             font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
        frame = tk.Frame(register_window, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)
        tk.Label(frame, text="Full Name:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=15, padx=20)
        full_name = tk.Entry(frame, font=("Arial", 14), width=30)
        full_name.grid(row=0, column=1, pady=15, padx=20)
        tk.Label(frame, text="Email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=1, column=0, pady=15, padx=20)
        email = tk.Entry(frame, font=("Arial", 14), width=30)
        email.grid(row=1, column=1, pady=15, padx=20)
        tk.Label(frame, text="Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=2, column=0, pady=15, padx=20)
        password = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
        password.grid(row=2, column=1, pady=15, padx=20)
        tk.Label(frame, text="Confirm Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=3, column=0, pady=15, padx=20)
        confirm_password = tk.Entry(frame, show="*", font=("Arial", 14), width=30)
        confirm_password.grid(row=3, column=1, pady=15, padx=20)

        def register_action():
            user_full_name = full_name.get().strip()
            user_email = email.get().strip()
            user_password = password.get()
            user_confirm_password = confirm_password.get()
            if not user_full_name or not user_email or not user_password or not user_confirm_password:
                messagebox.showerror("Error", "Please fill all fields!")
                return
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, user_email):
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            if user_password != user_confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            if len(user_password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long!")
                return
            if not re.search(r'\d', user_password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', user_password):
                messagebox.showerror("Error", "Password must contain at least one number and one special character!")
                return
            try:
                if self.client is None:
                    raise Exception("DB client not available")
                if self.client['user_auth_db']['Email_users'].find_one({"email": user_email}):
                    messagebox.showerror("Error", "Email already registered!")
                    return
                hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
                self.client['user_auth_db']['Email_users'].insert_one({
                    "full_name": user_full_name,
                    "email": user_email,
                    "password": hashed_password,
                    "created_at": datetime.datetime.now(),
                    "last_login": None
                })
                messagebox.showinfo("Success", "Registration Successful! You can now login.")
                register_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {e}")

    def show_forgot_password(self):
        forgot_window = tk.Toplevel(self.root)
        forgot_window.title("Forgot Password")
        forgot_window.geometry("450x250")
        forgot_window.configure(bg="#f0f0f0")
        back_btn = tk.Button(forgot_window, text="←", command=forgot_window.destroy,
                             font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
        frame = tk.Frame(forgot_window, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)
        tk.Label(frame, text="Enter your registered email:", bg="#f0f0f0",
                 font=("Arial", 14)).grid(row=0, column=0, pady=10, padx=10)
        email = tk.Entry(frame, font=("Arial", 14), width=30)
        email.grid(row=0, column=1, pady=10, padx=10)

        def reset_password_action():
            user_email = email.get().strip()
            if not user_email:
                messagebox.showerror("Error", "Please enter your email")
                return
            try:
                if self.client is None:
                    raise Exception("DB client not available")
                user = self.client['user_auth_db']['Email_users'].find_one({"email": user_email})
                if not user:
                    messagebox.showerror("Error", "Email not found in our records")
                    return
                messagebox.showinfo("Success", "If your email is registered, you will receive password reset instructions shortly.")
                forgot_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"DB error: {e}")

    # ----------------------- Dashboard -----------------------
    def show_dashboard(self):
        dashboard = tk.Toplevel(self.root)
        dashboard.title("Employee Management Dashboard")
        dashboard.geometry("1350x700+0+0")
        dashboard.configure(bg="#2c3e50")

        # Sidebar
        sidebar = tk.Frame(dashboard, bg="#2c3e50", width=200, height=700)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="Home", font=("Arial", 20, "bold"),
                 bg="#2c3e50", fg="white", pady=50).pack(fill=tk.X)
        tk.Button(sidebar, text="← Back to Login", command=dashboard.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=5, side=tk.TOP)

        tk.Button(sidebar, text="Employee Management", command=lambda: self.show_employee_management(dashboard),
                  bg="#34495e", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=20)

        tk.Button(sidebar, text="Search Employee", command=lambda: self.show_search_window(dashboard),
                  bg="#34495e", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=20)

        tk.Button(sidebar, text="Export Data", command=lambda: self.show_export_window(dashboard),
                  bg="#34495e", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=20)

        tk.Button(sidebar, text="Reports", command=lambda: self.show_reports_window(dashboard),
                  bg="#34495e", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=20)

        tk.Button(sidebar, text="Settings", command=lambda: self.show_settings_window(dashboard),
                  bg="#34495e", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=20)

        tk.Button(sidebar, text="Logout", command=dashboard.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12), bd=0, pady=10, width=20).pack(fill=tk.X, pady=5, side=tk.BOTTOM)

        # Main content
        content_frame = tk.Frame(dashboard, bg="#ecf0f1")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(content_frame,
                 text="Welcome to the Employee Management Dashboard",
                 font=("Arial", 24, "bold"),
                 bg="#ecf0f1", fg="#2c3e50",
                 pady=20).pack(pady=30)

        stats_frame = tk.Frame(content_frame, bg="#ecf0f1")
        stats_frame.pack(pady=20)

        # Use safe counts (if DB unavailable, show 0)
        try:
            emp_db = self.client['employee_management'] if self.client else None
            emp_collection = emp_db['employees'] if emp_db else None
            total_employees = emp_collection.count_documents({}) if emp_collection else 0
            active_count = emp_collection.count_documents({"status": "Active"}) if emp_collection else 0
            inactive_count = emp_collection.count_documents({"status": "Inactive"}) if emp_collection else 0
            new_this_month = emp_collection.count_documents({"created_at": {"$gte": datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0)}}) if emp_collection else 0
        except Exception:
            total_employees = active_count = inactive_count = new_this_month = 0

        self.create_stat_box(stats_frame, "Total Employees", str(total_employees), "#3498db", 0, 0)
        self.create_stat_box(stats_frame, "Active Employees", str(active_count), "#2ecc71", 0, 1)
        self.create_stat_box(stats_frame, "Inactive Employees", str(inactive_count), "#e74c3c", 1, 0)
        self.create_stat_box(stats_frame, "New This Month", str(new_this_month), "#f39c12", 1, 1)

        # Load employee management by default
        self.show_employee_management(dashboard)

    def create_stat_box(self, parent, title, value, color, row, col):
        box = tk.Frame(parent, bg=color, width=200, height=100, padx=20, pady=20)
        box.grid(row=row, column=col, padx=10, pady=10)
        box.grid_propagate(False)
        tk.Label(box, text=title, font=("Arial", 12), bg=color, fg="white").pack(anchor="w")
        tk.Label(box, text=value, font=("Arial", 24, "bold"), bg=color, fg="white").pack(anchor="center", pady=10)

    # ----------------------- Employee Management -----------------------
    def show_employee_management(self, parent):
        # Clear main area except sidebar
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()

        # ensure we have DB references
        if self.client:
            self.db = self.client['employee_management']
            self.collection = self.db['employees']
        else:
            self.db = None
            self.collection = None

        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(main_frame, text="Employee Management", font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50").pack(pady=20)

        # Content frame
        content_frame = tk.Frame(main_frame, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Form frame
        form_frame = tk.Frame(content_frame, bg="white", bd=2, relief=tk.RIDGE)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(form_frame, text="Employee Details", font=("Arial", 16, "bold"),
                 bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        # Entry variables
        self.var_emp_id = tk.StringVar()
        self.var_designation = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_dob = tk.StringVar()
        self.var_doj = tk.StringVar()
        self.var_age = tk.StringVar()
        self.var_experience = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_proof_id = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_contact = tk.StringVar()
        self.var_hired_location = tk.StringVar()
        self.var_status = tk.StringVar()
        self.var_address = tk.StringVar()

        fields_frame = tk.Frame(form_frame, bg="white")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Row 1
        tk.Label(fields_frame, text="Employee ID", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_emp_id, font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=1, pady=5, padx=5, sticky="w")

        # Row 2
        tk.Label(fields_frame, text="Name", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_name, font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=1, pady=5, padx=5, sticky="w")
        tk.Label(fields_frame, text="Designation", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=1, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_designation, font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=3, pady=5, padx=5, sticky="w")

        # Row 3
        tk.Label(fields_frame, text="DOB", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_dob, font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=1, pady=5, padx=5, sticky="w")
        tk.Label(fields_frame, text="DOJ", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=2, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_doj, font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=3, pady=5, padx=5, sticky="w")

        # Row 4
        tk.Label(fields_frame, text="Age", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_age, font=("Arial", 12), bg="#f0f0f0").grid(row=3, column=1, pady=5, padx=5, sticky="w")
        tk.Label(fields_frame, text="Gender", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=3, column=2, sticky="w", pady=5, padx=10)
        gender_combo = ttk.Combobox(fields_frame, textvariable=self.var_gender, font=("Arial", 12), state="readonly", values=("Male", "Female", "Other"))
        gender_combo.grid(row=3, column=3, pady=5, padx=5, sticky="w")
        gender_combo.current(0)

        # Row 5
        tk.Label(fields_frame, text="Experience", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_experience, font=("Arial", 12), bg="#f0f0f0").grid(row=4, column=1, pady=5, padx=5, sticky="w")
        tk.Label(fields_frame, text="Proof ID", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=4, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_proof_id, font=("Arial", 12), bg="#f0f0f0").grid(row=4, column=3, pady=5, padx=5, sticky="w")

        # Row 6
        tk.Label(fields_frame, text="Email", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=5, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_email, font=("Arial", 12), bg="#f0f0f0").grid(row=5, column=1, pady=5, padx=5, sticky="w")
        tk.Label(fields_frame, text="Contact", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=5, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_contact, font=("Arial", 12), bg="#f0f0f0").grid(row=5, column=3, pady=5, padx=5, sticky="w")

        # Row 7
        tk.Label(fields_frame, text="Hired Location", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=6, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_hired_location, font=("Arial", 12), bg="#f0f0f0").grid(row=6, column=1, pady=5, padx=5, sticky="w")
        tk.Label(fields_frame, text="Status", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=6, column=2, sticky="w", pady=5, padx=10)
        status_combo = ttk.Combobox(fields_frame, textvariable=self.var_status, font=("Arial", 12), state="readonly", values=("Active", "Inactive", "On Leave"))
        status_combo.grid(row=6, column=3, pady=5, padx=5, sticky="w")
        status_combo.current(0)

        # Row 8
        tk.Label(fields_frame, text="Address", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=7, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_address, font=("Arial", 12), bg="#f0f0f0", width=50).grid(row=7, column=1, columnspan=3, pady=5, padx=5, sticky="w")

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        save_btn = tk.Button(btn_frame, text="Save", command=self.save_data,
                             bg="#2ecc71", fg="white", font=("Arial", 12), width=10)
        save_btn.grid(row=0, column=0, padx=5)
        update_btn = tk.Button(btn_frame, text="Update", command=self.update_data,
                               bg="#3498db", fg="white", font=("Arial", 12), width=10)
        update_btn.grid(row=0, column=1, padx=5)
        delete_btn = tk.Button(btn_frame, text="Delete", command=self.delete_data,
                               bg="#e74c3c", fg="white", font=("Arial", 12), width=10)
        delete_btn.grid(row=0, column=2, padx=5)
        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_data,
                              bg="#95a5a6", fg="white", font=("Arial", 12), width=10)
        clear_btn.grid(row=0, column=3, padx=5)

        # Table Frame
        table_frame = tk.Frame(content_frame, bg="white", bd=2, relief=tk.RIDGE)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(table_frame, text="Employee Records", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        scroll_frame = tk.Frame(table_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_x = Scrollbar(scroll_frame, orient=HORIZONTAL)
        scroll_y = Scrollbar(scroll_frame, orient=VERTICAL)

        self.employee_table = ttk.Treeview(scroll_frame,
                                           columns=("emp_id", "name", "designation", "age", "gender",
                                                    "experience", "email", "contact", "hired_location", "status", "address", "proof_id", "created_at", "updated_at","doj", "dob"),
                                           xscrollcommand=scroll_x.set,
                                           yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.employee_table.xview)
        scroll_y.config(command=self.employee_table.yview)

        # headings
        headings = [("emp_id","EMP ID"),("name","Name"),("designation","Designation"),("age","Age"),("gender","Gender"),
                    ("experience","Experience"),("email","Email"),("contact","Contact"),("hired_location","Hired Location"),
                    ("status","Status"),("address","Address"),("proof_id","Proof ID"),("created_at","Created At"),
                    ("updated_at","Updated At"),("doj","DOJ"),("dob","DOB")]
        for col, text in headings:
            self.employee_table.heading(col, text=text)
        for col, width in [("emp_id",100),("name",150),("designation",150),("age",50),("gender",80),
                           ("experience",100),("email",150),("contact",100),("hired_location",150),("status",100),
                           ("address",200),("proof_id",150),("created_at",150),("updated_at",150),("doj",100),("dob",100)]:
            self.employee_table.column(col, width=width)
        self.employee_table["show"] = "headings"
        self.employee_table.pack(fill=BOTH, expand=1)
        self.employee_table.bind("<ButtonRelease-1>", self.get_data)

        # Start by loading data in background
        self.run_fetch_data_thread()

    # ----------------------- Data load / table population (thread-safe) -----------------------
    def run_fetch_data_thread(self):
        threading.Thread(target=self.fetch_data_thread, daemon=True).start()

    def fetch_data_thread(self):
        try:
            if not self.collection:
                records = []
            else:
                records = list(self.collection.find())
        except Exception as e:
            records = []
            print("Error fetching data:", e)
        # schedule UI update
        self.root.after(0, lambda: self.populate_employee_table(records))

    def populate_employee_table(self, records):
        # clear
        for item in self.employee_table.get_children():
            self.employee_table.delete(item)
        for record in records:
            self.employee_table.insert("", "end", values=(
                record.get("emp_id", ""),
                record.get("name", ""),
                record.get("designation", ""),
                record.get("age", ""),
                record.get("gender", ""),
                record.get("experience", ""),
                record.get("email", ""),
                record.get("contact", ""),
                record.get("hired_location", ""),
                record.get("status", ""),
                record.get("address", ""),
                record.get("proof_id", ""),
                record.get("created_at", ""),
                record.get("updated_at", ""),
                record.get("doj", ""),
                record.get("dob", "")
            ))

    # ----------------------- Table interaction -----------------------
    def get_data(self, event):
        selected_row = self.employee_table.focus()
        data = self.employee_table.item(selected_row, "values")
        if data and self.collection:
            try:
                employee = self.collection.find_one({"emp_id": data[0]})
                if employee:
                    self.var_emp_id.set(employee.get("emp_id",""))
                    self.var_name.set(employee.get("name",""))
                    self.var_designation.set(employee.get("designation",""))
                    self.var_dob.set(employee.get("dob",""))
                    self.var_doj.set(employee.get("doj",""))
                    self.var_age.set(employee.get("age",""))
                    self.var_experience.set(employee.get("experience",""))
                    self.var_gender.set(employee.get("gender",""))
                    self.var_proof_id.set(employee.get("proof_id",""))
                    self.var_email.set(employee.get("email",""))
                    self.var_contact.set(employee.get("contact",""))
                    self.var_hired_location.set(employee.get("hired_location",""))
                    self.var_status.set(employee.get("status",""))
                    self.var_address.set(employee.get("address",""))
            except Exception as e:
                messagebox.showerror("Error", f"DB error: {e}")

    # ----------------------- CRUD -----------------------
    def save_data(self):
        if self.var_emp_id.get().strip() == "":
            messagebox.showerror("Error", "Employee ID is required")
            return
        if not self.collection:
            messagebox.showerror("Error", "Database not available")
            return
        try:
            if self.collection.find_one({"emp_id": self.var_emp_id.get()}):
                messagebox.showerror("Error", "Employee ID already exists")
                return
            employee_data = {
                "emp_id": self.var_emp_id.get().strip(),
                "designation": self.var_designation.get().strip(),
                "name": self.var_name.get().strip(),
                "dob": self.var_dob.get().strip(),
                "doj": self.var_doj.get().strip(),
                "age": self.var_age.get().strip(),
                "experience": self.var_experience.get().strip(),
                "gender": self.var_gender.get().strip(),
                "proof_id": self.var_proof_id.get().strip(),
                "email": self.var_email.get().strip(),
                "contact": self.var_contact.get().strip(),
                "hired_location": self.var_hired_location.get().strip(),
                "status": self.var_status.get().strip(),
                "address": self.var_address.get().strip(),
                "created_at": datetime.datetime.now()
            }
            self.collection.insert_one(employee_data)
            messagebox.showinfo("Success", "Record saved successfully!")
            self.run_fetch_data_thread()
        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {e}")

    def update_data(self):
        if self.var_emp_id.get().strip() == "":
            messagebox.showerror("Error", "Employee ID is required")
            return
        if not self.collection:
            messagebox.showerror("Error", "Database not available")
            return
        try:
            update_data = {
                "designation": self.var_designation.get().strip(),
                "name": self.var_name.get().strip(),
                "dob": self.var_dob.get().strip(),
                "doj": self.var_doj.get().strip(),
                "age": self.var_age.get().strip(),
                "experience": self.var_experience.get().strip(),
                "gender": self.var_gender.get().strip(),
                "proof_id": self.var_proof_id.get().strip(),
                "email": self.var_email.get().strip(),
                "contact": self.var_contact.get().strip(),
                "hired_location": self.var_hired_location.get().strip(),
                "status": self.var_status.get().strip(),
                "address": self.var_address.get().strip(),
                "updated_at": datetime.datetime.now()
            }
            self.collection.update_one({"emp_id": self.var_emp_id.get()}, {"$set": update_data})
            messagebox.showinfo("Success", "Record updated successfully!")
            self.clear_data()
            self.run_fetch_data_thread()
        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {e}")

    def delete_data(self):
        if self.var_emp_id.get().strip() == "":
            messagebox.showerror("Error", "Employee ID is required")
            return
        if not self.collection:
            messagebox.showerror("Error", "Database not available")
            return
        try:
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
            if confirm:
                self.collection.delete_one({"emp_id": self.var_emp_id.get()})
                messagebox.showinfo("Success", "Record deleted successfully!")
                self.clear_data()
                self.run_fetch_data_thread()
        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {e}")

    def clear_data(self):
        self.var_emp_id.set("")
        self.var_designation.set("")
        self.var_name.set("")
        self.var_dob.set("")
        self.var_doj.set("")
        self.var_age.set("")
        self.var_experience.set("")
        self.var_gender.set("")
        self.var_proof_id.set("")
        self.var_email.set("")
        self.var_contact.set("")
        self.var_hired_location.set("")
        self.var_status.set("")
        self.var_address.set("")

    # ----------------------- Search Window (threaded search) -----------------------
    def show_search_window(self, parent):
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()

        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(),
                             font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
        tk.Label(main_frame, text="Search Employee Records", font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50").pack(pady=20)

        search_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        search_options = ["Employee ID", "Name", "Designation", "Status", "Hired Location", "Email", "Contact", "Proof ID", "Address", "DOB", "DOJ", "Age", "Experience", "Gender", "Created At", "Updated At"]
        tk.Label(search_frame, text="Search By:", font=("Arial", 12), bg="white", fg="#2c3e50", pady=10, padx=10).grid(row=0, column=0)

        self.search_by = tk.StringVar()
        search_combo = ttk.Combobox(search_frame, textvariable=self.search_by, font=("Arial", 12), state="readonly", values=search_options)
        search_combo.grid(row=0, column=1, padx=10, pady=10)
        search_combo.current(0)
        self.search_text = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_text, font=("Arial", 12), bg="#f0f0f0", width=30)
        search_entry.grid(row=0, column=2, padx=10, pady=10)

        # Buttons use threaded wrappers
        search_btn = tk.Button(search_frame, text="Search", command=self.run_search_thread,
                               bg="#3498db", fg="white", font=("Arial", 12), width=10)
        search_btn.grid(row=0, column=3, padx=10, pady=10)
        show_all_btn = tk.Button(search_frame, text="Show All", command=self.run_fetch_all_thread,
                                 bg="#2ecc71", fg="white", font=("Arial", 12), width=10)
        show_all_btn.grid(row=0, column=4, padx=10, pady=10)

        # Results area
        results_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(results_frame, text="Search Results", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        scroll_frame = tk.Frame(results_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_x = Scrollbar(scroll_frame, orient=HORIZONTAL)
        scroll_y = Scrollbar(scroll_frame, orient=VERTICAL)
        self.search_table = ttk.Treeview(scroll_frame,
                                         columns=("emp_id", "name", "designation", "age", "gender",
                                                  "experience", "email", "contact", "status", "created_at", "updated_at", "hired_location", "proof_id", "address", "dob", "doj"),
                                         xscrollcommand=scroll_x.set,
                                         yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.search_table.xview)
        scroll_y.config(command=self.search_table.yview)

        for col, txt in [("emp_id","EMP ID"),("name","Name"),("designation","Designation"),("age","Age"),("gender","Gender"),
                         ("experience","Experience"),("email","Email"),("contact","Contact"),("status","Status"),
                         ("created_at","Created At"),("updated_at","Updated At"),("hired_location","Hired Location"),
                         ("proof_id","Proof ID"),("address","Address"),("dob","DOB"),("doj","DOJ")]:
            self.search_table.heading(col, text=txt)
        # widths
        self.search_table.pack(fill=BOTH, expand=1)
        self.search_table.bind("<Double-1>", self.view_full_details)
        # load all initially via thread
        self.run_fetch_all_thread()

    def run_search_thread(self):
        threading.Thread(target=self.search_employee_thread, daemon=True).start()

    def search_employee_thread(self):
        search_by = self.search_by.get()
        search_text = self.search_text.get().strip()
        # map
        field_map = {
            "Employee ID": "emp_id", "Name": "name", "Designation": "designation",
            "Hired Location": "hired_location","Proof ID":"proof_id","Address":"address",
            "DOB":"dob","DOJ":"doj","Status":"status","Email":"email","Contact":"contact",
            "Age":"age","Experience":"experience","Gender":"gender","Created At":"created_at","Updated At":"updated_at"
        }
        field = field_map.get(search_by)
        if not search_text:
            # show message on UI thread
            self.root.after(0, lambda: messagebox.showinfo("Info", "Please enter search text"))
            return
        query = {field: {"$regex": search_text, "$options": "i"}}
        try:
            if not self.db:
                results = []
            else:
                results = list(self.db['employees'].find(query))
        except Exception as e:
            results = []
            print("Search error:", e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Search error: {e}"))
        # schedule UI update
        self.root.after(0, lambda: self.populate_search_table(results))

    def populate_search_table(self, records):
        for item in self.search_table.get_children():
            self.search_table.delete(item)
        for record in records:
            self.search_table.insert("", "end", values=(
                record.get("emp_id", ""),
                record.get("name", ""),
                record.get("designation", ""),
                record.get("age", ""),
                record.get("gender", ""),
                record.get("experience", ""),
                record.get("email", ""),
                record.get("contact", ""),
                record.get("status", ""),
                record.get("created_at", ""),
                record.get("updated_at", ""),
                record.get("hired_location", ""),
                record.get("proof_id", ""),
                record.get("address", ""),
                record.get("dob", ""),
                record.get("doj", "")
            ))
        if len(self.search_table.get_children()) == 0:
            messagebox.showinfo("Info", "No matching records found")

    def run_fetch_all_thread(self):
        threading.Thread(target=self.fetch_all_employees_thread, daemon=True).start()

    def fetch_all_employees_thread(self):
        try:
            if not self.db:
                results = []
            else:
                results = list(self.db['employees'].find())
        except Exception as e:
            results = []
            print("Fetch all error:", e)
        self.root.after(0, lambda: self.populate_search_table(results))

    def view_full_details(self, event):
        selected_row = self.search_table.focus()
        data = self.search_table.item(selected_row, "values")
        if data:
            try:
                employee = self.db['employees'].find_one({"emp_id": data[0]}) if self.db else None
            except Exception as e:
                employee = None
                print("DB error:", e)
            details_window = tk.Toplevel()
            details_window.title(f"Employee Details - {data[1]}")
            details_window.geometry("600x500")
            details_window.configure(bg="#f0f0f0")
            details_frame = tk.Frame(details_window, bg="white", bd=2, relief=tk.RIDGE)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            tk.Label(details_frame, text=f"Details for {employee.get('name','') if employee else data[1]}",
                   font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
            info_frame = tk.Frame(details_frame, bg="white")
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            row = 0
            if employee:
                for key, value in employee.items():
                    if key not in ["_id", "created_at", "updated_at"]:
                        tk.Label(info_frame, text=key.replace("_", " ").title() + ":",
                               font=("Arial", 12, "bold"), bg="white", fg="#2c3e50", anchor="w").grid(row=row, column=0, sticky="w", pady=5)
                        tk.Label(info_frame, text=str(value),
                               font=("Arial", 12), bg="white", fg="#34495e", anchor="w").grid(row=row, column=1, sticky="w", pady=5, padx=10)
                        row += 1
            else:
                tk.Label(info_frame, text="No further details available", bg="white").pack()
            tk.Button(details_window, text="Close", command=details_window.destroy,
                      bg="#e74c3c", fg="white", font=("Arial", 12), width=10).pack(pady=10)

    # ----------------------- Export / Preview (thread-safe) -----------------------
    def show_export_window(self, parent):
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(),
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
        tk.Label(main_frame, text="Export Employee Data", font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50").pack(pady=20)
        export_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(export_frame, text="Export Options", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        options_frame = tk.Frame(export_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(options_frame, text="Export Format:", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=10)
        self.export_format = tk.StringVar()
        format_combo = ttk.Combobox(options_frame, textvariable=self.export_format, font=("Arial", 12), state="readonly", values=("CSV", "PDF"))
        format_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        format_combo.current(0)
        tk.Label(options_frame, text="Data to Export:", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=10)
        self.export_data = tk.StringVar()
        data_combo = ttk.Combobox(options_frame, textvariable=self.export_data, font=("Arial", 12), state="readonly", values=("All Employees", "Active Employees", "Inactive Employees"))
        data_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        data_combo.current(0)
        btn_frame = tk.Frame(options_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        export_btn = tk.Button(btn_frame, text="Export", command=self.run_export_action_thread,
                             bg="#3498db", fg="white", font=("Arial", 12), width=15)
        export_btn.grid(row=0, column=0, padx=10)
        preview_btn = tk.Button(btn_frame, text="Preview Data", command=self.run_preview_thread,
                              bg="#2ecc71", fg="white", font=("Arial", 12), width=15)
        preview_btn.grid(row=0, column=1, padx=10)

        preview_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(preview_frame, text="Data Preview", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)

        scroll_frame = tk.Frame(preview_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_x = Scrollbar(scroll_frame, orient=HORIZONTAL)
        scroll_y = Scrollbar(scroll_frame, orient=VERTICAL)
        self.preview_table = ttk.Treeview(scroll_frame,
                                       columns=("emp_id", "name", "designation", "status", "address", "email", "contact", "proof_id", "hired_location", "doj", "dob", "age", "experience", "gender", "created_at", "updated_at"),
                                       xscrollcommand=scroll_x.set,
                                       yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.preview_table.xview)
        scroll_y.config(command=self.preview_table.yview)
        for col, txt in [("emp_id","EMP ID"),("name","Name"),("designation","Designation"),("status","Status"),("address","Address"),
                         ("email","Email"),("contact","Contact"),("proof_id","Proof ID"),("hired_location","Hired Location"),
                         ("doj","Date of Joining"),("dob","Date of Birth"),("age","Age"),("experience","Experience"),("gender","Gender"),
                         ("created_at","Created At"),("updated_at","Updated At")]:
            self.preview_table.heading(col, text=txt)
        # configure widths
        for col, width in [("emp_id",100),("name",150),("designation",150),("status",100),
                           ("address",200),("email",200),("contact",150),("proof_id",150),
                           ("hired_location",150),("doj",150),("dob",150),("age",100),
                           ("experience",100),("gender",100),("created_at",150),("updated_at",150)]:
            self.preview_table.column(col, width=width)
        self.preview_table["show"] = "headings"
        self.preview_table.pack(fill=BOTH, expand=1)

    # Preview/export threading wrappers
    def run_preview_thread(self):
        threading.Thread(target=self.preview_export_data_thread, daemon=True).start()

    def preview_export_data_thread(self):
        # determine query
        query = {}
        if self.export_data.get() == "Active Employees":
            query = {"status": "Active"}
        elif self.export_data.get() == "Inactive Employees":
            query = {"status": "Inactive"}
        try:
            if not self.db:
                data = []
            else:
                data = list(self.db['employees'].find(query))
        except Exception as e:
            data = []
            print("Preview error:", e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Preview error: {e}"))
        # schedule UI update
        self.root.after(0, lambda: self.populate_preview_table(data))

    def populate_preview_table(self, records):
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)
        for record in records:
            self.preview_table.insert("", "end", values=(
                record.get("emp_id",""),
                record.get("name",""),
                record.get("designation",""),
                record.get("status",""),
                record.get("address",""),
                record.get("email",""),
                record.get("contact",""),
                record.get("proof_id",""),
                record.get("hired_location",""),
                record.get("doj",""),
                record.get("dob",""),
                record.get("age",""),
                record.get("experience",""),
                record.get("gender",""),
                record.get("created_at",""),
                record.get("updated_at","")
            ))

    # Export action wrapper
    def run_export_action_thread(self):
        threading.Thread(target=self.export_data_action_thread, daemon=True).start()

    def export_data_action_thread(self):
        export_format = self.export_format.get()
        export_data_type = self.export_data.get()
        # build query
        query = {}
        if export_data_type == "Active Employees":
            query = {"status": "Active"}
        elif export_data_type == "Inactive Employees":
            query = {"status": "Inactive"}
        try:
            if not self.db:
                data = []
            else:
                data = list(self.db['employees'].find(query))
        except Exception as e:
            data = []
            print("Export fetch error:", e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Export fetch error: {e}"))
            return

        if not data:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No data to export"))
            return

        if export_format == "CSV":
            # run actual write in thread (we're already in thread)
            try:
                file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                         filetypes=[("CSV files", "*.csv")],
                                                         initialfile=f"{export_data_type.replace(' ','_')}.csv")
                if not file_path:
                    return
                # write CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["emp_id", "name", "designation", "age", "gender",
                                  "experience", "email", "contact", "hired_location",
                                  "status", "address", "proof_id", "dob", "doj", "created_at", "updated_at"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in data:
                        # convert datetimes to string safely
                        rec = {k: (v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime.datetime) else v)
                               for k, v in record.items() if k in fieldnames}
                        writer.writerow(rec)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Data exported successfully to {file_path}"))
                # ask to open file on UI thread
                def ask_open():
                    if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                        try:
                            os.startfile(file_path)
                        except Exception as e:
                            messagebox.showerror("Error", f"Cannot open file: {e}")
                self.root.after(0, ask_open)
            except Exception as e:
                print("CSV export error:", e)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting CSV: {e}"))
        else:
            # PDF export
            try:
                file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                         filetypes=[("PDF files", "*.pdf")],
                                                         initialfile=f"{export_data_type.replace(' ','_')}.pdf")
                if not file_path:
                    return
                # Build PDF (this may be slow — already in thread)
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                title = Paragraph(f"Employee Data - {export_data_type}", styles['Title'])
                elements.append(title)
                elements.append(Paragraph(" ", styles['Normal']))
                # table header
                table_data = [["Emp ID", "Name", "Designation", "Status", "Email", "DOB", "Experience", "Gender"]]
                for record in data:
                    table_data.append([
                        record.get("emp_id",""),
                        record.get("name",""),
                        record.get("designation",""),
                        record.get("status",""),
                        record.get("email",""),
                        record.get("dob",""),
                        record.get("experience",""),
                        record.get("gender","")
                    ])
                table = Table(table_data)
                style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                    ('BOTTOMPADDING',(0,0),(-1,0),12),
                    ('BACKGROUND',(0,1),(-1,-1),colors.beige),
                    ('GRID',(0,0),(-1,-1),1,colors.black)
                ])
                table.setStyle(style)
                elements.append(table)
                elements.append(Paragraph(" ", styles['Normal']))
                timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
                elements.append(timestamp)
                doc.build(elements)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Data exported successfully to {file_path}"))
                def ask_open_pdf():
                    if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                        try:
                            os.startfile(file_path)
                        except Exception as e:
                            messagebox.showerror("Error", f"Cannot open file: {e}")
                self.root.after(0, ask_open_pdf)
            except Exception as e:
                print("PDF export error:", e)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting PDF: {e}"))

    # ----------------------- Reports (cards) -----------------------
    def show_reports_window(self, parent):
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(),
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
        tk.Label(main_frame, text="Employee Reports", font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50").pack(pady=20)
        reports_frame = tk.Frame(main_frame, bg="#ecf0f1")
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        # Create cards (Use threaded wrappers for heavy reports)
        self.create_report_card(reports_frame, "Employee Status Report", "View distribution of employees by status", self.run_status_report_thread, 0, 0)
        self.create_report_card(reports_frame, "Department Distribution", "View employees by department/designation", self.run_department_report_thread, 0, 1)
        self.create_report_card(reports_frame, "Experience Analysis", "View employee experience distribution", self.run_experience_report_thread, 1, 0)
        self.create_report_card(reports_frame, "Location Distribution", "View employees by hired location", self.run_location_report_thread, 1, 1)
        self.create_report_card(reports_frame, "Age Analysis", "View employee age distribution", self.run_age_report_thread, 2, 0)
        self.create_report_card(reports_frame, "Gender Distribution", "View employee gender distribution", self.run_gender_report_thread, 2, 1)
        self.create_report_card(reports_frame, "Proof ID Distribution", "View employee proof ID distribution", self.run_proof_id_report_thread, 3, 0)
        self.create_report_card(reports_frame, "Export Data", "Export employee data to CSV/PDF", lambda: self.show_export_window(parent), 3, 1)
        self.create_report_card(reports_frame, "Exit", "Exit the application", self.exit_action, 4, 0)

    def create_report_card(self, parent, title, description, command, row, col):
        card = tk.Frame(parent, bg="white", bd=1, relief=tk.RIDGE, width=300, height=160)
        card.grid(row=row, column=col, padx=20, pady=20)
        card.grid_propagate(False)
        tk.Label(card, text=title, font=("Arial", 14, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        tk.Label(card, text=description, font=("Arial", 10), bg="white", fg="#7f8c8d", wraplength=250).pack(fill=tk.X, padx=10)
        tk.Button(card, text="View Report", command=command, bg="#3498db", fg="white", font=("Arial", 10)).pack(pady=10)

    def exit_action(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    # ----------------------- Report generators (thread wrappers + implementations) -----------------------
    def run_status_report_thread(self):
        threading.Thread(target=self.show_status_report, daemon=True).start()

    def show_status_report(self):
        report_window = tk.Toplevel()
        report_window.title("Employee Status Report")
        report_window.geometry("600x500")
        report_window.configure(bg="#f0f0f0")
        tk.Label(report_window, text="Employee Status Distribution", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)
        try:
            if not self.db:
                active_count = inactive_count = on_leave_count = 0
            else:
                active_count = self.db['employees'].count_documents({"status": "Active"})
                inactive_count = self.db['employees'].count_documents({"status": "Inactive"})
                on_leave_count = self.db['employees'].count_documents({"status": "On Leave"})
        except Exception as e:
            print("Status report error:", e)
            active_count = inactive_count = on_leave_count = 0
        report_frame = tk.Frame(report_window, bg="white", bd=2, relief=tk.RIDGE)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(report_frame, text=f"Active Employees: {active_count}", font=("Arial", 14), bg="white", fg="#2ecc71", pady=10).pack(fill=tk.X, padx=20)
        tk.Label(report_frame, text=f"Inactive Employees: {inactive_count}", font=("Arial", 14), bg="white", fg="#e74c3c", pady=10).pack(fill=tk.X, padx=20)
        tk.Label(report_frame, text=f"Employees on Leave: {on_leave_count}", font=("Arial", 14), bg="white", fg="#f39c12", pady=10).pack(fill=tk.X, padx=20)
        total = active_count + inactive_count + on_leave_count
        tk.Label(report_frame, text=f"Total Employees: {total}", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X, padx=20)
        tk.Button(report_window, text="Export Report", command=lambda: threading.Thread(target=self.export_status_report, args=(active_count, inactive_count, on_leave_count), daemon=True).start(), bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)

    def export_status_report(self, active, inactive, on_leave):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")], initialfile="Employee_Status_Report.pdf")
            if not file_path:
                return
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            title = Paragraph("Employee Status Distribution Report", styles['Title'])
            elements.append(title)
            elements.append(Paragraph(" ", styles['Normal']))
            table_data = [["Status", "Count", "Percentage"]]
            total = active + inactive + on_leave if (active+inactive+on_leave) > 0 else 1
            table_data.append(["Active", str(active), f"{(active/total)*100:.2f}%"])
            table_data.append(["Inactive", str(inactive), f"{(inactive/total)*100:.2f}%"])
            table_data.append(["On Leave", str(on_leave), f"{(on_leave/total)*100:.2f}%"])
            table_data.append(["Total", str(active+inactive+on_leave), "100.00%"])
            table = Table(table_data)
            style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('BOTTOMPADDING',(0,0),(-1,0),12),
                ('BACKGROUND',(0,1),(-1,-1),colors.beige),
                ('GRID',(0,0),(-1,-1),1,colors.black),
                ('BACKGROUND',(0,-1),(-1,-1),colors.lightblue),
                ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
            ])
            table.setStyle(style)
            elements.append(table)
            elements.append(Paragraph(" ", styles['Normal']))
            timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            elements.append(timestamp)
            doc.build(elements)
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Report exported successfully to {file_path}"))
            def ask_open():
                if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                    try:
                        os.startfile(file_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Cannot open file: {e}")
            self.root.after(0, ask_open)
        except Exception as e:
            print("Export status report error:", e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting report: {e}"))

    # department report
    def run_department_report_thread(self):
        threading.Thread(target=self.show_department_report, daemon=True).start()

    def show_department_report(self):
        report_window = tk.Toplevel()
        report_window.title("Department Distribution Report")
        report_window.geometry("600x500")
        report_window.configure(bg="#f0f0f0")
        tk.Label(report_window, text="Employee Department Distribution", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)
        try:
            if not self.db:
                department_data = []
            else:
                pipeline = [
                    {"$group": {"_id": "$designation", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]
                department_data = list(self.db['employees'].aggregate(pipeline))
        except Exception as e:
            print("Department report error:", e)
            department_data = []
        report_frame = tk.Frame(report_window, bg="white", bd=2, relief=tk.RIDGE)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scroll_frame = tk.Frame(report_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_y = Scrollbar(scroll_frame, orient=VERTICAL)
        dept_table = ttk.Treeview(scroll_frame, columns=("department","count"), yscrollcommand=scroll_y.set)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=dept_table.yview)
        dept_table.heading("department", text="Department/Designation")
        dept_table.heading("count", text="Number of Employees")
        dept_table.column("department", width=300)
        dept_table.column("count", width=200)
        dept_table["show"] = "headings"
        dept_table.pack(fill=BOTH, expand=1)
        total = 0
        for dept in department_data:
            dept_table.insert("", "end", values=(dept["_id"] if dept["_id"] else "Not Specified", dept["count"]))
            total += dept["count"]
        tk.Label(report_window, text=f"Total Employees: {total}", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=5)
        tk.Button(report_window, text="Export Report", command=lambda: threading.Thread(target=self.export_department_report, args=(department_data,), daemon=True).start(), bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)

    def export_department_report(self, department_data):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")], initialfile="Department_Distribution_Report.pdf")
            if not file_path:
                return
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            title = Paragraph("Employee Department Distribution Report", styles['Title'])
            elements.append(title)
            elements.append(Paragraph(" ", styles['Normal']))
            table_data = [["Department/Designation", "Count", "Percentage"]]
            total = sum(dept["count"] for dept in department_data) if department_data else 0
            for dept in department_data:
                dept_name = dept["_id"] if dept["_id"] else "Not Specified"
                count = dept["count"]
                percentage = (count/total)*100 if total > 0 else 0
                table_data.append([dept_name, str(count), f"{percentage:.2f}%"])
            table_data.append(["Total", str(total), "100.00%"])
            table = Table(table_data)
            style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('BOTTOMPADDING',(0,0),(-1,0),12),
                ('BACKGROUND',(0,1),(-1,-1),colors.beige),
                ('GRID',(0,0),(-1,-1),1,colors.black),
                ('BACKGROUND',(0,-1),(-1,-1),colors.lightblue),
                ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
            ])
            table.setStyle(style)
            elements.append(table)
            elements.append(Paragraph(" ", styles['Normal']))
            timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            elements.append(timestamp)
            doc.build(elements)
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Report exported successfully to {file_path}"))
            def ask_open():
                if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                    try:
                        os.startfile(file_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Cannot open file: {e}")
            self.root.after(0, ask_open)
        except Exception as e:
            print("Export department report error:", e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting report: {e}"))

    # Experience report (thread wrapper)
    def run_experience_report_thread(self):
        threading.Thread(target=self.show_experience_report, daemon=True).start()

    def show_experience_report(self):
        # This method is heavy (DB fetch + processing). We're already in a thread.
        report_window = tk.Toplevel()
        report_window.title("Experience Profile Analytics")
        report_window.geometry("700x500")
        report_window.configure(bg="#f0f0f0")
        tk.Label(report_window, text="Employee Experience Distribution Analysis", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)
        try:
            if not self.db:
                employees = []
            else:
                employees = list(self.db['employees'].find({}, {"name":1, "designation":1, "experience":1}))
        except Exception as e:
            print("Experience fetch error:", e)
            employees = []
        # categorize
        categories = {
            "Less than 1 year": 0,
            "1-3 years": 0,
            "3-5 years": 0,
            "5-10 years": 0,
            "10+ years": 0,
            "Not specified": 0
        }
        categorized_employees = {k: [] for k in categories.keys()}

        def categorize_experience(employee):
            exp_value = employee.get("experience","")
            if not exp_value:
                return "Not specified"
            exp_str = str(exp_value).strip().lower()
            try:
                years = float(exp_str)
                if years < 1:
                    return "Less than 1 year"
                elif years < 3:
                    return "1-3 years"
                elif years < 5:
                    return "3-5 years"
                elif years < 10:
                    return "5-10 years"
                else:
                    return "10+ years"
            except Exception:
                pass
            import re
            number_match = re.search(r'(\d+\.?\d*)', exp_str)
            if number_match:
                try:
                    years = float(number_match.group(1))
                    if years < 1:
                        return "Less than 1 year"
                    elif years < 3:
                        return "1-3 years"
                    elif years < 5:
                        return "3-5 years"
                    elif years < 10:
                        return "5-10 years"
                    else:
                        return "10+ years"
                except Exception:
                    pass
            range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', exp_str)
            if range_match:
                try:
                    min_y = float(range_match.group(1))
                    max_y = float(range_match.group(2))
                    avg_y = (min_y + max_y) / 2
                    if avg_y < 1:
                        return "Less than 1 year"
                    elif avg_y < 3:
                        return "1-3 years"
                    elif avg_y < 5:
                        return "3-5 years"
                    elif avg_y < 10:
                        return "5-10 years"
                    else:
                        return "10+ years"
                except Exception:
                    pass
            if "less than 1" in exp_str or "<1" in exp_str:
                return "Less than 1 year"
            elif any(x in exp_str for x in ["1-3","1 to 3","1 - 3"]):
                return "1-3 years"
            elif any(x in exp_str for x in ["3-5","3 to 5","3 - 5"]):
                return "3-5 years"
            elif any(x in exp_str for x in ["5-10","5 to 10","5 - 10"]):
                return "5-10 years"
            elif "10+" in exp_str or ">10" in exp_str or "more than 10" in exp_str:
                return "10+ years"
            return "Not specified"

        for emp in employees:
            cat = categorize_experience(emp)
            categories[cat] += 1
            categorized_employees[cat].append(emp)

        # Now update UI — schedule the heavy UI creation on main thread
        def build_ui():
            main_container = tk.Frame(report_window, bg="white", bd=2, relief=tk.RIDGE)
            main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            left_panel = tk.Frame(main_container, bg="white", width=300)
            left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
            left_panel.pack_propagate(False)
            right_panel = tk.Frame(main_container, bg="white")
            right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            tk.Label(left_panel, text="Experience Summary", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=5)
            total_employees = len(employees)
            summary_frame = tk.Frame(left_panel, bg="white")
            summary_frame.pack(fill=tk.X, pady=5)
            tk.Label(summary_frame, text="Experience Range", font=("Arial", 11, "bold"), bg="#3498db", fg="white").grid(row=0, column=0, sticky="ew", padx=1, pady=1)
            tk.Label(summary_frame, text="Count", font=("Arial", 11, "bold"), bg="#3498db", fg="white").grid(row=0, column=1, sticky="ew", padx=1, pady=1)
            tk.Label(summary_frame, text="Percentage", font=("Arial", 11, "bold"), bg="#3498db", fg="white").grid(row=0, column=2, sticky="ew", padx=1, pady=1)
            row_idx = 1
            for category, count in categories.items():
                bg_color = "#f9f9f9" if row_idx % 2 == 0 else "white"
                percentage = (count / total_employees) * 100 if total_employees > 0 else 0
                tk.Label(summary_frame, text=category, font=("Arial", 10), bg=bg_color).grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
                tk.Label(summary_frame, text=str(count), font=("Arial", 10), bg=bg_color).grid(row=row_idx, column=1, padx=5, pady=1)
                tk.Label(summary_frame, text=f"{percentage:.2f}%", font=("Arial", 10), bg=bg_color).grid(row=row_idx, column=2, padx=5, pady=1)
                row_idx += 1
            tk.Label(summary_frame, text="Total", font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
            tk.Label(summary_frame, text=str(total_employees), font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=row_idx, column=1, padx=5, pady=1)
            tk.Label(summary_frame, text="100.00%", font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=row_idx, column=2, padx=5, pady=1)

            tk.Label(right_panel, text="Employee List", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=5)
            tk.Label(right_panel, text="Select Experience Range:", font=("Arial", 11), bg="white").pack(anchor="w", padx=5)
            selected_range = tk.StringVar()
            range_dropdown = ttk.Combobox(right_panel, textvariable=selected_range, values=list(categories.keys()), state="readonly", width=30)
            range_dropdown.pack(anchor="w", padx=5, pady=5)
            if list(categories.keys()):
                range_dropdown.current(0)
            employee_count_var = tk.StringVar(value=f"Employees: {categories[list(categories.keys())[0]] if list(categories.keys()) else 0}")
            employee_count = tk.Label(right_panel, textvariable=employee_count_var, font=("Arial", 11, "bold"), bg="white", fg="#2c3e50")
            employee_count.pack(anchor="w", padx=5, pady=5)
            list_frame = tk.Frame(right_panel, bg="white")
            list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            scroll_y = Scrollbar(list_frame, orient=VERTICAL)
            emp_list = tk.Listbox(list_frame, font=("Arial", 11), height=15, yscrollcommand=scroll_y.set)
            scroll_y.config(command=emp_list.yview)
            scroll_y.pack(side=RIGHT, fill=Y)
            emp_list.pack(fill=BOTH, expand=True)

            def update_employee_list(*args):
                emp_list.delete(0, tk.END)
                selected = selected_range.get()
                if selected:
                    emps = categorized_employees[selected]
                    count = len(emps)
                    employee_count_var.set(f"Employees: {count}")
                    if count == 0:
                        emp_list.insert(tk.END, "No employees in this category")
                    else:
                        for emp in emps:
                            name = emp.get("name","Unknown")
                            designation = emp.get("designation","Unknown")
                            experience = emp.get("experience","Not specified")
                            emp_list.insert(tk.END, f"{name} - {designation} - {experience}")
            selected_range.trace("w", update_employee_list)
            update_employee_list()
            tk.Button(report_window, text="Export Report", command=lambda: threading.Thread(target=self.export_simple_experience_report, args=(categories, categorized_employees, total_employees), daemon=True).start(), bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)

        # schedule UI build
        self.root.after(0, build_ui)

    def export_simple_experience_report(self, categories, categorized_employees, total_employees):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     filetypes=[("PDF files", ".pdf"), ("CSV files", ".csv")],
                                                     initialfile="Employee_Experience_Analysis.pdf")
            if not file_path:
                return
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                # write csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Experience Range", "Number of Employees", "Percentage", "Employee Names"])
                    for category, count in categories.items():
                        percentage = (count / total_employees) * 100 if total_employees > 0 else 0
                        employee_names = [emp.get("name","Unknown") for emp in categorized_employees[category]]
                        names_str = ", ".join(employee_names)
                        writer.writerow([category, count, f"{percentage:.2f}%", names_str])
                    writer.writerow(["Total", total_employees, "100.00%", ""])
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Report exported successfully to {file_path}"))
                def ask_open():
                    if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                        try:
                            os.startfile(file_path)
                        except Exception as e:
                            messagebox.showerror("Error", f"Cannot open file: {e}")
                self.root.after(0, ask_open)
            else:
                # PDF
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                title = Paragraph("Employee Experience Distribution Analysis", styles['Title'])
                elements.append(title)
                elements.append(Paragraph(" ", styles['Normal']))
                summary_text = Paragraph("This report provides an analysis of employee experience distribution across the organization.", styles['Normal'])
                elements.append(summary_text)
                elements.append(Paragraph(" ", styles['Normal']))
                table_data = [["Experience Range", "Number of Employees", "Percentage"]]
                for category, count in categories.items():
                    percentage = (count / total_employees) * 100 if total_employees > 0 else 0
                    table_data.append([category, str(count), f"{percentage:.2f}%"])
                table_data.append(["Total", str(total_employees), "100.00%"])
                table = Table(table_data)
                style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                    ('BOTTOMPADDING',(0,0),(-1,0),12),
                    ('BACKGROUND',(0,1),(-1,-1),colors.beige),
                    ('GRID',(0,0),(-1,-1),1,colors.black),
                    ('BACKGROUND',(0,-1),(-1,-1),colors.lightblue),
                    ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
                ])
                table.setStyle(style)
                elements.append(table)
                elements.append(Paragraph(" ", styles['Normal']))
                elements.append(Paragraph("Detailed Employee Lists by Experience Category", styles['Heading2']))
                for category, employees in categorized_employees.items():
                    if employees:
                        elements.append(Paragraph(" ", styles['Normal']))
                        elements.append(Paragraph(f"{category} ({len(employees)} employees)", styles['Heading3']))
                        emp_data = [["Name", "Designation", "Experience"]]
                        for emp in employees:
                            emp_data.append([emp.get("name","Unknown"), emp.get("designation","Unknown"), str(emp.get("experience","Not specified"))])
                        emp_table = Table(emp_data)
                        emp_style = TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                            ('ALIGN',(0,0),(-1,-1),'LEFT'),
                            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                            ('BOTTOMPADDING',(0,0),(-1,0),6),
                            ('GRID',(0,0),(-1,-1),1,colors.lightgrey)
                        ])
                        emp_table.setStyle(emp_style)
                        elements.append(emp_table)
                elements.append(Paragraph(" ", styles['Normal']))
                timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
                elements.append(timestamp)
                doc.build(elements)
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Report exported successfully to {file_path}"))
                def ask_open_pdf():
                    if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                        try:
                            os.startfile(file_path)
                        except Exception as e:
                            messagebox.showerror("Error", f"Cannot open file: {e}")
                self.root.after(0, ask_open_pdf)
        except Exception as e:
            print("Export experience report error:", e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting report: {e}"))

    # location report (simple placeholder)
    def run_location_report_thread(self):
        threading.Thread(target=self.show_location_report, daemon=True).start()

    def show_location_report(self):
        messagebox.showinfo("Coming Soon", "Location Distribution Report is under development")

    # simple wrappers for other report placeholders
    def run_age_report_thread(self):
        threading.Thread(target=lambda: messagebox.showinfo("Coming Soon", "Age Analysis under development"), daemon=True).start()

    def run_gender_report_thread(self):
        threading.Thread(target=lambda: messagebox.showinfo("Coming Soon", "Gender Distribution under development"), daemon=True).start()

    def run_proof_id_report_thread(self):
        threading.Thread(target=lambda: messagebox.showinfo("Coming Soon", "Proof ID Distribution under development"), daemon=True).start()

    # ----------------------- Settings and change password -----------------------
    def show_settings_window(self, parent):
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(),
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
        tk.Label(main_frame, text="Settings", font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50").pack(pady=20)
        settings_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(settings_frame, text="Application Settings", font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        options_frame = tk.Frame(settings_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        tk.Label(options_frame, text="Database Settings", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=10, columnspan=2)
        tk.Label(options_frame, text="MongoDB Connection String:", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=5)
        self.connection_string = tk.StringVar(value=db_url if db_url else "")
        tk.Entry(options_frame, textvariable=self.connection_string, font=("Arial", 12), bg="#f0f0f0", width=50).grid(row=1, column=1, pady=5, padx=5, sticky="w")
        tk.Label(options_frame, text="Change Password", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").grid(row=2, column=0, sticky="w", pady=10, columnspan=2)
        tk.Button(options_frame, text="Change Password", command=self.show_change_password, bg="#3498db", fg="white", font=("Arial", 10)).grid(row=3, column=1, pady=5, padx=5, sticky="w")
        tk.Label(options_frame, text="Theme:", font=("Arial", 12), bg="white", fg="#2c3e50").grid(row=4, column=0, sticky="w", pady=5)
        self.theme = tk.StringVar(value="Light")
        theme_combo = ttk.Combobox(options_frame, textvariable=self.theme, font=("Arial", 12), state="readonly", values=("Light","Dark"))
        theme_combo.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        tk.Button(settings_frame, text="Save Settings", command=self.save_settings, bg="#2ecc71", fg="white", font=("Arial", 12), width=15).pack(pady=20)

    def show_change_password(self):
        password_window = tk.Toplevel()
        password_window.title("Change Password")
        password_window.geometry("400x300")
        password_window.configure(bg="#f0f0f0")
        frame = tk.Frame(password_window, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)
        tk.Label(frame, text="Current Password:", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=10)
        current_password = tk.Entry(frame, show="*", font=("Arial", 12), width=20)
        current_password.grid(row=0, column=1, pady=10, padx=10)
        tk.Label(frame, text="New Password:", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10)
        new_password = tk.Entry(frame, show="*", font=("Arial", 12), width=20)
        new_password.grid(row=1, column=1, pady=10, padx=10)
        tk.Label(frame, text="Confirm Password:", bg="#f0f0f0", font=("Arial", 12)).grid(row=2, column=0, pady=10, padx=10)
        confirm_password = tk.Entry(frame, show="*", font=("Arial", 12), width=20)
        confirm_password.grid(row=2, column=1, pady=10, padx=10)

        def change_password_action():
            if not current_password.get() or not new_password.get() or not confirm_password.get():
                messagebox.showerror("Error", "All fields are required")
                return
            if new_password.get() != confirm_password.get():
                messagebox.showerror("Error", "New password and confirm password do not match")
                return
            # NOTE: In this demo there's no active "current user" tracking.
            # Replace below with actual logic to locate current user.
            try:
                if not self.users_collection:
                    raise Exception("User DB not available")
                # for demo, find a user with this password (not ideal in real app)
                user = self.users_collection.find_one({})
                if user and bcrypt.checkpw(current_password.get().encode('utf-8'), user['password']):
                    hashed = bcrypt.hashpw(new_password.get().encode('utf-8'), bcrypt.gensalt())
                    self.users_collection.update_one({"_id": user["_id"]}, {"$set": {"password": hashed}})
                    messagebox.showinfo("Success", "Password changed successfully")
                    password_window.destroy()
                else:
                    messagebox.showerror("Error", "Current password is incorrect (demo logic)")
            except Exception as e:
                messagebox.showerror("Error", f"Error changing password: {e}")

        tk.Button(frame, text="Change Password", command=change_password_action, bg="#3498db", fg="white", font=("Arial", 12), width=15).grid(row=3, column=0, columnspan=2, pady=20)

    def save_settings(self):
        connection_string = self.connection_string.get().strip()
        theme = self.theme.get()
        # Save settings to .env or a config file could be implemented here.
        # For safety we just show a message — changing DB string at runtime requires reconnect logic.
        messagebox.showinfo("Success", "Settings saved successfully (note: change of DB string requires restart to take effect).")
        if theme == "Dark":
            self.root.configure(bg="#2c3e50")
        else:
            self.root.configure(bg="#f0f0f0")

# ----------------------- Main -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AuthenticationApp(root)
    root.mainloop()

