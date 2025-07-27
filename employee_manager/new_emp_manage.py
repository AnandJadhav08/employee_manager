# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "bcrypt",
#     "pandas",
#     "pymongo",
#     "reportlab",
# ]
# ///
import re
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox, filedialog
from pymongo import MongoClient
import bcrypt
import datetime
import csv
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
# from dotenv import load_dotenv
import os

# load_dotenv()

# db_url = os.getenv("DB_URL")

# MongoDB Connection
client = MongoClient('db_url')
db = client['user_auth_db']
users_collection = db['Email_users']

class AuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Data Management System | Developed by Anand and Payal")
        self.root.geometry("1350x700+0+0")
        self.root.configure(bg="#cacaca")
        
        
        # Button Frame in top right corner
        button_frame = tk.Frame(root, bg="#cacaca")
        button_frame.pack(anchor='ne', padx=10, pady=10)
        
        # Smaller buttons with reduced width and height
        tk.Button(button_frame, text="Admin", command=self.show_login_frame,
                 bg="#4CAF50", fg="white", font=("Arial", 10), width=10, height=1).pack(side=tk.LEFT, padx=5)
        
        
        tk.Button(button_frame, text="Register", command=self.show_register_frame,
                 bg="#2196F3", fg="white", font=("Arial", 10), width=10, height=1).pack(side=tk.LEFT)

        # Welcome Text Frame
        welcome_frame = tk.Frame(root, bg="#cacaca")
        welcome_frame.pack(expand=True)
        
        # Main Welcome Text
        tk.Label(welcome_frame, 
                text="Welcome to Our Employee Data Management System",
                font=("Helvetica", 40, "bold"),
                fg="#0d4f70",
                bg="#cacaca").pack(pady=10)
        
        # Subtitle Text
        tk.Label(welcome_frame,
                text="Your Gateway to Seamless Authentication",
                font=("Georgia", 18, "italic"),
                fg="dark green",
                bg="#cacaca").pack(pady=5)
        
        # Additional decorative line
        tk.Label(welcome_frame,
                text="✦ ━━━━━━━━━━━━━━━ ✦",
                font=("Arial", 16),
                fg="#000000",
                bg="#cacaca").pack(pady=20)
        

    def show_login_frame(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Admin Login")
        login_window.geometry("1350x700+0+0")
        login_window.configure(bg="#cacaca")
        
          # Add back arrow button
        back_btn = tk.Button(login_window, text="←", command=login_window.destroy, 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        frame = tk.Frame(login_window, bg="#f0f0f0")
        frame.pack(expand=True)
        
        tk.Label(frame, text="Email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=20, padx=20)
        email = tk.Entry(frame, font=("Arial", 14), width=25)
        email.grid(row=0, column=1, pady=20, padx=20)
        
        tk.Label(frame, text="Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=1, column=0, pady=20, padx=20)
        password = tk.Entry(frame, show="*", font=("Arial", 14), width=25)
        password.grid(row=1, column=1, pady=20, padx=20)
        
        # Add password requirements hint
        password_hint = tk.Label(frame, text="Password must be at least 6 characters with numbers and symbols", 
                               bg="#f0f0f0", font=("Arial", 10), fg="#666666")
        password_hint.grid(row=2, column=0, columnspan=2, pady=5)
        
        def login_action():
            user_email = email.get()
            user_password = password.get()
            
            if not user_email or not user_password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            # Email validation using simple regex
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, user_email):
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
            # Find user by email instead of username
            user = users_collection.find_one({"email": user_email})
            
            if user and bcrypt.checkpw(user_password.encode('utf-8'), user['password']):
                messagebox.showinfo("Success", "Login Successful!")
                
                # Update last login timestamp
                users_collection.update_one(
                    {"email": user_email},
                    {"$set": {"last_login": datetime.datetime.now()}}
                )
                
                login_window.destroy()
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid Email or Password")
        
        tk.Button(frame, text="Login", command=login_action,
                 bg="#4CAF50", fg="white", font=("Arial", 14), width=20).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Add forgot password link
        forgot_password = tk.Label(frame, text="Forgot Password?", bg="#f0f0f0", 
                                 font=("Arial", 10, "underline"), fg="#0000FF", cursor="hand2")
        forgot_password.grid(row=4, column=0, columnspan=2)
        forgot_password.bind("<Button-1>", lambda e: self.show_forgot_password())
    
    def show_register_frame(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("1350x700+0+0")
        register_window.configure(bg="#cacaca")
        
     # Add back arrow button
        back_btn = tk.Button(register_window, text="←", command=register_window.destroy, 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)
    

        frame = tk.Frame(register_window, bg="#f0f0f0")
        frame.pack(expand=True)
        
        tk.Label(frame, text="Full Name:", bg="#f0f0f0", font=("Arial", 14)).grid(row=0, column=0, pady=15, padx=20)
        full_name = tk.Entry(frame, font=("Arial", 14), width=25)
        full_name.grid(row=0, column=1, pady=15, padx=20)
        
        tk.Label(frame, text="Email:", bg="#f0f0f0", font=("Arial", 14)).grid(row=1, column=0, pady=15, padx=20)
        email = tk.Entry(frame, font=("Arial", 14), width=25)
        email.grid(row=1, column=1, pady=15, padx=20)
        
        tk.Label(frame, text="Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=2, column=0, pady=15, padx=20)
        password = tk.Entry(frame, show="*", font=("Arial", 14), width=25)
        password.grid(row=2, column=1, pady=15, padx=20)
        
        tk.Label(frame, text="Confirm Password:", bg="#f0f0f0", font=("Arial", 14)).grid(row=3, column=0, pady=15, padx=20)
        confirm_password = tk.Entry(frame, show="*", font=("Arial", 14), width=25)
        confirm_password.grid(row=3, column=1, pady=15, padx=20)
        
        # Password requirements hint
        password_hint = tk.Label(frame, 
                               text="Password must be at least 6 characters with numbers and symbols", 
                               bg="#f0f0f0", font=("Arial", 10), fg="#666666")
        password_hint.grid(row=4, column=0, columnspan=2, pady=5)
        
        def register_action():
            user_full_name = full_name.get()
            user_email = email.get()
            user_password = password.get()#f
            user_confirm_password = confirm_password.get()
            
            # Validate all fields are filled
            if not user_full_name or not user_email or not user_password or not user_confirm_password:
                messagebox.showerror("Error", "Please fill all fields!")
                return
            
            # Email validation using regex
            import re
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, user_email):
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
            # Check if passwords match
            if user_password != user_confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            
            # Password strength validation
            if len(user_password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long!")
                return
            
            # Check for at least one number and one special character
            if not re.search(r'\d', user_password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', user_password):
                messagebox.showerror("Error", "Password must contain at least one number and one special character!")
                return
            
            # Check if email already exists
            if users_collection.find_one({"email": user_email}):
                messagebox.showerror("Error", "Email already registered!")
                return
            
            # All validations passed, create new user
            try:
                hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
                users_collection.insert_one({
                    "full_name": user_full_name,
                    "email": user_email,
                    "password": hashed_password,
                    "created_at": datetime.datetime.now(),
                    "last_login": None
                })
                messagebox.showinfo("Success", "Registration Successful! You can now login.")
                register_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
        
        tk.Button(frame, text="Register", command=register_action,
                 bg="#2196F3", fg="white", font=("Arial", 14), width=20).grid(row=5, column=0, columnspan=2, pady=20)
    
    def show_forgot_password(self):
        forgot_window = tk.Toplevel(self.root)
        forgot_window.title("Forgot Password")
        forgot_window.geometry("450x250")
        forgot_window.configure(bg="#f0f0f0")

        # Add back arrow button with square box and color
        back_btn = tk.Button(forgot_window, text="←", command=forgot_window.destroy, 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        frame = tk.Frame(forgot_window, bg="#f0f0f0")
        frame.pack(expand=True)
        
        tk.Label(frame, text="Enter your registered email:", bg="#f0f0f0", 
               font=("Arial", 14)).grid(row=0, column=0, pady=20, padx=20)
        
        email = tk.Entry(frame, font=("Arial", 14), width=25)
        email.grid(row=0, column=1, pady=20, padx=20)
        
        def reset_password_action():
            user_email = email.get()
            
            if not user_email:
                messagebox.showerror("Error", "Please enter your email")
                return
            
            # Check if email exists
            user = users_collection.find_one({"email": user_email})
            if not user:
                messagebox.showerror("Error", "Email not found in our records")
                return
            
            # In a real application, you would send a password reset email here
            # For this demo, we'll just show a message
            messagebox.showinfo("Success", 
                              "If your email is registered, you will receive password reset instructions shortly.")
            forgot_window.destroy()
        
        tk.Button(frame, text="Reset Password", command=reset_password_action,
                 bg="#FF9800", fg="white", font=("Arial", 14), width=15).grid(row=1, column=0, columnspan=2, pady=20)

    def show_dashboard(self):
        # Create a new window for the dashboard
        dashboard = tk.Toplevel(self.root)
        dashboard.title("Employee Management Dashboard")
        dashboard.geometry("1350x700+0+0")
        dashboard.configure(bg="#2c3e50")
        
        # Create a sidebar frame
        sidebar = tk.Frame(dashboard, bg="#2c3e50", width=200, height=700)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Dashboard title
        tk.Label(sidebar, text="Home", font=("Arial", 20, "bold"), 
                bg="#2c3e50", fg="white", pady=50).pack(fill=tk.X)
        
        # Sidebar buttons

        # Add back/exit button at the top of sidebar
        back_btn = tk.Button(sidebar, text="← Back to Login", 
                       command=dashboard.destroy,
                       bg="#e74c3c", fg="white", font=("Arial", 12), 
                       bd=0, pady=10, width=20)
        back_btn.pack(fill=tk.X, pady=5, side=tk.TOP)
    
        btn_employee = tk.Button(sidebar, text="Employee Management", 
                               command=lambda: self.show_employee_management(dashboard),
                               bg="#34495e", fg="white", font=("Arial", 12), 
                               bd=0, pady=10, width=20)
        btn_employee.pack(fill=tk.X, pady=20)
        
        btn_search = tk.Button(sidebar, text="Search Employee", 
                             command=lambda: self.show_search_window(dashboard),
                             bg="#34495e", fg="white", font=("Arial", 12), 
                             bd=0, pady=10, width=20)
        btn_search.pack(fill=tk.X, pady=20)
        
        btn_export = tk.Button(sidebar, text="Export Data", 
                             command=lambda: self.show_export_window(dashboard),
                             bg="#34495e", fg="white", font=("Arial", 12), 
                             bd=0, pady=10, width=20)
        btn_export.pack(fill=tk.X, pady=20)
        
        btn_reports = tk.Button(sidebar, text="Reports", 
                              command=lambda: self.show_reports_window(dashboard),
                              bg="#34495e", fg="white", font=("Arial", 12), 
                              bd=0, pady=10, width=20)
        btn_reports.pack(fill=tk.X, pady=20)
        
        btn_settings = tk.Button(sidebar, text="Settings", 
                               command=lambda: self.show_settings_window(dashboard),
                               bg="#34495e", fg="white", font=("Arial", 12), 
                               bd=0, pady=10, width=20)
        btn_settings.pack(fill=tk.X, pady=20)
        
        btn_logout = tk.Button(sidebar, text="Logout", 
                             command=dashboard.destroy,
                             bg="#e74c3c", fg="white", font=("Arial", 12), 
                             bd=0, pady=10, width=20)
        btn_logout.pack(fill=tk.X, pady=5, side=tk.BOTTOM)
        
        # Main content area
        content_frame = tk.Frame(dashboard, bg="#ecf0f1")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Welcome message in the content area
        tk.Label(content_frame, 
                text="Welcome to the Employee Management Dashboard",
                font=("Arial", 24, "bold"),
                bg="#ecf0f1", fg="#2c3e50",
                pady=20).pack(pady=30)
        
        # Dashboard stats in a grid
        stats_frame = tk.Frame(content_frame, bg="#ecf0f1")
        stats_frame.pack(pady=20)
        
        # MongoDB Connection for dashboard stats
        emp_db = client['employee_management']
        emp_collection = emp_db['employees']
        
        # Count total employees
        total_employees = emp_collection.count_documents({})
        
        # Create stat boxes
        self.create_stat_box(stats_frame, "Total Employees", str(total_employees), "#3498db", 0, 0)
        self.create_stat_box(stats_frame, "Active Employees", 
                           str(emp_collection.count_documents({"status": "Active"})), "#2ecc71", 0, 1)
        self.create_stat_box(stats_frame, "Inactive Employees", 
                           str(emp_collection.count_documents({"status": "Inactive"})), "#e74c3c", 1, 0)
        self.create_stat_box(stats_frame, "New This Month", 
                           str(emp_collection.count_documents({
                               "created_at": {"$gte": datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0)}
                           })), "#f39c12", 1, 1)
        
        # Show the employee management screen by default
        self.show_employee_management(dashboard)
    
    def create_stat_box(self, parent, title, value, color, row, col):
        box = tk.Frame(parent, bg=color, width=200, height=100, padx=20, pady=20)
        box.grid(row=row, column=col, padx=10, pady=10)
        box.grid_propagate(False)  # Prevent the frame from shrinking
        
        tk.Label(box, text=title, font=("Arial", 12), bg=color, fg="white").pack(anchor="w")
        tk.Label(box, text=value, font=("Arial", 24, "bold"), bg=color, fg="white").pack(anchor="center", pady=10)
    
    def show_employee_management(self, parent):
        # Clear any existing content in the main area
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        
        # MongoDB Connection
        self.client = MongoClient('db_url')
        self.db = self.client['employee_management']
        self.collection = self.db['employees']
        
        # Main content frame
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Employee Management", 
                             font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50")
        title_label.pack(pady=20)
        
        # Create a frame for the form and table
        content_frame = tk.Frame(main_frame, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Form frame
        form_frame = tk.Frame(content_frame, bg="white", bd=2, relief=RIDGE)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form title
        tk.Label(form_frame, text="Employee Details", font=("Arial", 16, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Entry Variables
        self.var_emp_id = StringVar()
        self.var_designation = StringVar()
        self.var_name = StringVar()
        self.var_dob = StringVar()
        self.var_doj = StringVar()
        self.var_age = StringVar()
        self.var_experience = StringVar()
        self.var_gender = StringVar()
        self.var_proof_id = StringVar()
        self.var_email = StringVar()
        self.var_contact = StringVar()
        self.var_hired_location = StringVar()
        self.var_status = StringVar()
        self.var_address = StringVar()
        self.var_created_at = StringVar()
        self.var_updated_at = StringVar()
        
        # Create form fields
        fields_frame = tk.Frame(form_frame, bg="white")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Row 1
        tk.Label(fields_frame, text="Employee ID", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=0, column=0,sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_emp_id, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        # Row 2
        tk.Label(fields_frame, text="Name", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_name, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        tk.Label(fields_frame, text="Designation", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=1, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_designation, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=1, column=3, pady=5, padx=5, sticky="w")
        
        # Row 3
        tk.Label(fields_frame, text="DOB", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_dob, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        tk.Label(fields_frame, text="DOJ", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=2, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_doj, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=2, column=3, pady=5, padx=5, sticky="w")
        
        # Row 4
        tk.Label(fields_frame, text="Age", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_age, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=3, column=1, pady=5, padx=5, sticky="w")
        
        tk.Label(fields_frame, text="Gender", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=3, column=2, sticky="w", pady=5, padx=10)
        gender_combo = ttk.Combobox(fields_frame, textvariable=self.var_gender, font=("Arial", 12),
                                  state="readonly", values=("Male", "Female", "Other"))
        gender_combo.grid(row=3, column=3, pady=5, padx=5, sticky="w")
        gender_combo.current(0)
        
        # Row 5
        tk.Label(fields_frame, text="Experience", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_experience, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=4, column=1, pady=5, padx=5, sticky="w")
        
        tk.Label(fields_frame, text="Proof ID", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=4, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_proof_id, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=4, column=3, pady=5, padx=5, sticky="w")
        
        # Row 6
        tk.Label(fields_frame, text="Email", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=5, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_email, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=5, column=1, pady=5, padx=5, sticky="w")
        
        tk.Label(fields_frame, text="Contact", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=5, column=2, sticky="w", pady=5, padx=10)
        tk.Entry(fields_frame, textvariable=self.var_contact, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=5, column=3, pady=5, padx=5, sticky="w")
        
        # Row 7
        tk.Label(fields_frame, text="Hired Location", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=6, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_hired_location, font=("Arial", 12), 
                bg="#f0f0f0").grid(row=6, column=1, pady=5, padx=5, sticky="w")
        
        tk.Label(fields_frame, text="Status", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=6, column=2, sticky="w", pady=5, padx=10)
        status_combo = ttk.Combobox(fields_frame, textvariable=self.var_status, font=("Arial", 12),
                                  state="readonly", values=("Active", "Inactive", "On Leave"))
        status_combo.grid(row=6, column=3, pady=5, padx=5, sticky="w")
        status_combo.current(0)
        
        # Row 8
        tk.Label(fields_frame, text="Address", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=7, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.var_address, font=("Arial", 12), 
                bg="#f0f0f0", width=50).grid(row=7, column=1, columnspan=3, pady=5, padx=5, sticky="w")
        
        # Buttons Frame
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # CRUD Buttons
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
        table_frame = tk.Frame(content_frame, bg="white", bd=2, relief=RIDGE)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Table title
        tk.Label(table_frame, text="Employee Records", font=("Arial", 16, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Create table with scrollbars
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
        
        # Configure column headings
        self.employee_table.heading("emp_id", text="EMP ID")
        self.employee_table.heading("name", text="Name")
        self.employee_table.heading("designation", text="Designation")
        self.employee_table.heading("age", text="Age")
        self.employee_table.heading("gender", text="Gender")
        self.employee_table.heading("experience", text="Experience")
        self.employee_table.heading("email", text="Email")
        self.employee_table.heading("contact", text="Contact")
        self.employee_table.heading("hired_location", text="Hired Location")
        self.employee_table.heading("status", text="Status")
        self.employee_table.heading("address", text="Address")
        self.employee_table.heading("proof_id", text="Proof ID")
        self.employee_table.heading("created_at", text="Created At")
        self.employee_table.heading("updated_at", text="Updated At")
        self.employee_table.heading("doj", text="DOJ")
        self.employee_table.heading("dob", text="DOB")
        
        self.employee_table["show"] = "headings"
        
        
        # Configure column widths
        self.employee_table.column("emp_id", width=100)
        self.employee_table.column("name", width=150)
        self.employee_table.column("designation", width=150)
        self.employee_table.column("age", width=50)
        self.employee_table.column("gender", width=80)
        self.employee_table.column("experience", width=100)
        self.employee_table.column("email", width=150)
        self.employee_table.column("contact", width=100)
        self.employee_table.column("hired_location", width=150)
        self.employee_table.column("status", width=100)
        self.employee_table.column("address", width=200)
        self.employee_table.column("proof_id", width=150)
        self.employee_table.column("created_at", width=150)
        self.employee_table.column("updated_at", width=150)
        self.employee_table.column("doj", width=100)
        self.employee_table.column("dob", width=100)
        
        self.employee_table["show"] = "headings"
        self.employee_table.pack(fill=BOTH, expand=1)
        
        # Bind the treeview to a function to display selected data
        self.employee_table.bind("<ButtonRelease-1>", self.get_data)
        
        # Load data into the table
        self.fetch_data()
    
    def fetch_data(self):
        # Clear existing data
        for item in self.employee_table.get_children():
            self.employee_table.delete(item)
        
        # Fetch data from MongoDB
        data = self.collection.find()
        for record in data:
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
                # Add more fields as needed
            ))
    
    def get_data(self, event):
        # Get the selected item
        
        selected_row = self.employee_table.focus()
        data = self.employee_table.item(selected_row, "values")
        
        if data:
            # Get full employee data from MongoDB
            employee = self.collection.find_one({"emp_id": data[0]})
            
            # Set values to entry fields
            self.var_emp_id.set(employee.get("emp_id", ""))
            self.var_name.set(employee.get("name", ""))
            self.var_designation.set(employee.get("designation", ""))
            self.var_dob.set(employee.get("dob", ""))
            self.var_doj.set(employee.get("doj", ""))
            self.var_age.set(employee.get("age", ""))
            self.var_experience.set(employee.get("experience", ""))
            self.var_gender.set(employee.get("gender", ""))
            self.var_proof_id.set(employee.get("proof_id", ""))
            self.var_email.set(employee.get("email", ""))
            self.var_contact.set(employee.get("contact", ""))
            self.var_hired_location.set(employee.get("hired_location", ""))
            self.var_status.set(employee.get("status", ""))
            self.var_address.set(employee.get("address", ""))
            self.var_created_at.set(employee.get("created_at", ""))
            self.var_updated_at.set(employee.get("updated_at", ""))

            
            
    
    def save_data(self):
        if self.var_emp_id.get() == "":
            messagebox.showerror("Error", "Employee ID is required")
        else:
            try:
                # Check if employee already exists
                if self.collection.find_one({"emp_id": self.var_emp_id.get()}):
                    messagebox.showerror("Error", "Employee ID already exists")
                    return
                
                employee_data = {
                    "emp_id": self.var_emp_id.get(),
                    "designation": self.var_designation.get(),
                    "name": self.var_name.get(),
                    "dob": self.var_dob.get(),
                    "doj": self.var_doj.get(),
                    "age": self.var_age.get(),
                    "experience": self.var_experience.get(),
                    "gender": self.var_gender.get(),
                    "proof_id": self.var_proof_id.get(),
                    "email": self.var_email.get(),
                    "contact": self.var_contact.get(),
                    "hired_location": self.var_hired_location.get(),
                    "status": self.var_status.get(),
                    "address": self.var_address.get(),
                    "created_at": datetime.datetime.now()
                }
                self.collection.insert_one(employee_data)
                messagebox.showinfo("Success", "Record saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}")

    def update_data(self):
        if self.var_emp_id.get() == "":
            messagebox.showerror("Error", "Employee ID is required")
        else:
            try:
                # Create update dictionary with only non-empty fields
                update_data = {
                    "designation": self.var_designation.get(),
                    "name": self.var_name.get(),
                    "dob": self.var_dob.get(),
                    "doj": self.var_doj.get(),
                    "age": self.var_age.get(),
                    "experience": self.var_experience.get(),
                    "gender": self.var_gender.get(),
                    "proof_id": self.var_proof_id.get(),
                    "email": self.var_email.get(),
                    "contact": self.var_contact.get(),
                    "hired_location": self.var_hired_location.get(),
                    "status": self.var_status.get(),
                    "address": self.var_address.get(),
                    "updated_at": datetime.datetime.now()

                }
                
                self.collection.update_one(
                    {"emp_id": self.var_emp_id.get()},
                    {"$set": update_data}
                )
                messagebox.showinfo("Success", "Record updated successfully!")
                self.clear_data()
                self.fetch_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}")

    def delete_data(self):
        if self.var_emp_id.get() == "":
            messagebox.showerror("Error", "Employee ID is required")
        else:
            try:
                confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
                if confirm:
                    self.collection.delete_one({"emp_id": self.var_emp_id.get()})
                    messagebox.showinfo("Success", "Record deleted successfully!")
                    self.clear_data()
                    self.fetch_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}")

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

    def show_search_window(self, parent):
        # Clear any existing content in the main area
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        
        # Main content frame
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add back button with square box and color
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(), 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        # Title
        title_label = tk.Label(main_frame, text="Search Employee Records", 
                             font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50")
        title_label.pack(pady=20)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg="white", bd=2, relief=RIDGE)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Search options
        search_options = ["Employee ID", "Name", "Designation", "Status", "Hired Location", "Email", "Contact", "Proof ID", "Address", "DOB", "DOJ", "Age", "Experience", "Gender", "Created At", "Updated At"] 
        
        # Search by label
        tk.Label(search_frame, text="Search By:", font=("Arial", 12), 
               bg="white", fg="#2c3e50", pady=10, padx=10).grid(row=0, column=0)
        
        # Search option combobox
        self.search_by = StringVar()
        search_combo = ttk.Combobox(search_frame, textvariable=self.search_by, 
                                  font=("Arial", 12), state="readonly", values=search_options)
        search_combo.grid(row=0, column=1, padx=10, pady=10)
        search_combo.current(0)
        
        # Search text entry
        self.search_text = StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_text, 
                              font=("Arial", 12), bg="#f0f0f0", width=30)
        search_entry.grid(row=0, column=2, padx=10, pady=10)
        
        # Search button
        search_btn = tk.Button(search_frame, text="Search", command=self.search_employee, 
                             bg="#3498db", fg="white", font=("Arial", 12), width=10)
        search_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Show all button
        show_all_btn = tk.Button(search_frame, text="Show All", command=self.fetch_all_employees, 
                               bg="#2ecc71", fg="white", font=("Arial", 12), width=10)
        show_all_btn.grid(row=0, column=4, padx=10, pady=10)
        
        # Results frame
        results_frame = tk.Frame(main_frame, bg="white", bd=2, relief=RIDGE)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Results label
        tk.Label(results_frame, text="Search Results", font=("Arial", 16, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Create table with scrollbars
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
        
        # Configure column headings
        self.search_table.heading("emp_id", text="EMP ID")
        self.search_table.heading("name", text="Name")
        self.search_table.heading("designation", text="Designation")
        self.search_table.heading("age", text="Age")
        self.search_table.heading("gender", text="Gender")
        self.search_table.heading("experience", text="Experience")
        self.search_table.heading("email", text="Email")
        self.search_table.heading("contact", text="Contact")
        self.search_table.heading("status", text="Status")
        self.search_table.heading("created_at", text="Created At")
        self.search_table.heading("updated_at", text="Updated At")
        self.search_table.heading("hired_location", text="Hired Location")
        self.search_table.heading("proof_id", text="Proof ID")
        self.search_table.heading("address", text="Address")
        self.search_table.heading("dob", text="DOB")
        self.search_table.heading("doj", text="DOJ")
        
        # Configure column widths
        self.search_table.column("emp_id", width=100)
        self.search_table.column("name", width=150)
        self.search_table.column("designation", width=150)
        self.search_table.column("age", width=50)
        self.search_table.column("gender", width=80)
        self.search_table.column("experience", width=100)
        self.search_table.column("email", width=150)
        self.search_table.column("contact", width=100)
        self.search_table.column("status", width=100)
        self.search_table.column("created_at", width=150)
        self.search_table.column("updated_at", width=150)
        self.search_table.column("hired_location", width=150)
        self.search_table.column("proof_id", width=100)
        self.search_table.column("address", width=150)
        self.search_table.column("dob", width=100)
        self.search_table.column("doj", width=100)
        
        self.search_table["show"] = "headings"
        self.search_table.pack(fill=BOTH, expand=1)
        
        # Bind double click to view full details
        self.search_table.bind("<Double-1>", self.view_full_details)
        
        # Load all employees by default
        self.fetch_all_employees()
    
    def search_employee(self):
        search_by = self.search_by.get()
        search_text = self.search_text.get()
        
        # Clear existing data
        for item in self.search_table.get_children():
            self.search_table.delete(item)
        
        if not search_text:
            messagebox.showinfo("Info", "Please enter search text")
            return
        
        # Map search_by to MongoDB field
        field_map = {
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
            "Updated At": "updated_at"
        }
        
        field = field_map.get(search_by)
        
        # Create query with regex for partial match
        query = {field: {"$regex": search_text, "$options": "i"}}
        
        # Fetch data from MongoDB
        data = self.db['employees'].find(query)
        
        # Insert into table
        for record in data:
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
                record.get("doj", ""),


            ))
        
        # Show message if no results
        if len(self.search_table.get_children()) == 0:
            messagebox.showinfo("Info", "No matching records found")
    
    def fetch_all_employees(self):
        # Clear existing data
        for item in self.search_table.get_children():
            self.search_table.delete(item)
        
        # Fetch all data from MongoDB
        data = self.db['employees'].find()
        
        # Insert into table
        for record in data:
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
    
    def view_full_details(self, event):
        # Get selected item
        selected_row = self.search_table.focus()
        data = self.search_table.item(selected_row, "values")
        
        if data:
            # Create a new window for full details
            details_window = tk.Toplevel()
            details_window.title(f"Employee Details - {data[1]}")
            details_window.geometry("600x500")
            details_window.configure(bg="#f0f0f0")
            
            # Get full employee data from MongoDB
            employee = self.db['employees'].find_one({"emp_id": data[0]})
            
            # Create a frame for details
            details_frame = tk.Frame(details_window, bg="white", bd=2, relief=RIDGE)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            tk.Label(details_frame, text=f"Details for {employee.get('name', '')}", 
                   font=("Arial", 16, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
            
            # Create a grid for details
            info_frame = tk.Frame(details_frame, bg="white")
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Display all employee details
            row = 0
            for key, value in employee.items():
                if key not in ["_id", "created_at", "updated_at"]:
                    tk.Label(info_frame, text=key.replace("_", " ").title() + ":", 
                           font=("Arial", 12, "bold"), bg="white", fg="#2c3e50", 
                           anchor="w").grid(row=row, column=0, sticky="w", pady=5)
                    
                    tk.Label(info_frame, text=str(value), 
                           font=("Arial", 12), bg="white", fg="#34495e", 
                           anchor="w").grid(row=row, column=1, sticky="w", pady=5, padx=10)
                    row += 1
            
            # Close button
            tk.Button(details_window, text="Close", command=details_window.destroy, 
                    bg="#e74c3c", fg="white", font=("Arial", 12), width=10).pack(pady=10)

    def show_export_window(self, parent):
        # Clear any existing content in the main area
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        
        # Main content frame
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add back button with square box and color
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(), 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        # Title
        title_label = tk.Label(main_frame, text="Export Employee Data", 
                             font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50")
        title_label.pack(pady=20)
        
        # Export options frame
        export_frame = tk.Frame(main_frame, bg="white", bd=2, relief=RIDGE)
        export_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Export options label
        tk.Label(export_frame, text="Export Options", font=("Arial", 16, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Options frame
        options_frame = tk.Frame(export_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Export format
        tk.Label(options_frame, text="Export Format:", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=10)
        
        self.export_format = StringVar()
        format_combo = ttk.Combobox(options_frame, textvariable=self.export_format, 
                                  font=("Arial", 12), state="readonly", values=("CSV", "PDF"))
        format_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        format_combo.current(0)
        
        # Data selection
        tk.Label(options_frame, text="Data to Export:", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=10)
        
        self.export_data = StringVar()
        data_combo = ttk.Combobox(options_frame, textvariable=self.export_data, 
                                font=("Arial", 12), state="readonly", 
                                values=("All Employees", "Active Employees", "Inactive Employees"))
        data_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        data_combo.current(0)
        
        # Export buttons
        btn_frame = tk.Frame(options_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        export_btn = tk.Button(btn_frame, text="Export", command=self.export_data_action, 
                             bg="#3498db", fg="white", font=("Arial", 12), width=15)
        export_btn.grid(row=0, column=0, padx=10)
        
        preview_btn = tk.Button(btn_frame, text="Preview Data", command=self.preview_export_data, 
                              bg="#2ecc71", fg="white", font=("Arial", 12), width=15)
        preview_btn.grid(row=0, column=1, padx=10)
        
        # Preview frame
        preview_frame = tk.Frame(main_frame, bg="white", bd=2, relief=RIDGE)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Preview label
        tk.Label(preview_frame, text="Data Preview", font=("Arial", 16, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Create table with scrollbars
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
        
        # Configure column headings
        self.preview_table.heading("emp_id", text="EMP ID")
        self.preview_table.heading("name", text="Name")
        self.preview_table.heading("designation", text="Designation")
        self.preview_table.heading("status", text="Status")
        self.preview_table.heading("address", text="Address")
        self.preview_table.heading("email", text="Email")        
        self.preview_table.heading("contact", text="Contact")
        self.preview_table.heading("proof_id", text="Proof ID")
        self.preview_table.heading("hired_location", text="Hired Location")
        self.preview_table.heading("doj", text="Date of Joining")
        self.preview_table.heading("dob", text="Date of Birth")
        self.preview_table.heading("age", text="Age")
        self.preview_table.heading("experience", text="Experience")
        self.preview_table.heading("gender", text="Gender")
        self.preview_table.heading("created_at", text="Created At")
        self.preview_table.heading("updated_at", text="Updated At")
        

        # Configure column widths
        self.preview_table.column("emp_id", width=100)
        self.preview_table.column("name", width=150)
        self.preview_table.column("designation", width=150)
        self.preview_table.column("status", width=100)
        self.preview_table.column("address", width=200)
        self.preview_table.column("email", width=200)
        self.preview_table.column("contact", width=150)
        self.preview_table.column("proof_id", width=150)
        self.preview_table.column("hired_location", width=150)
        self.preview_table.column("doj", width=150)
        self.preview_table.column("dob", width=150)
        self.preview_table.column("age", width=100)
        self.preview_table.column("experience", width=100)
        self.preview_table.column("gender", width=100)
        self.preview_table.column("created_at", width=150)
        self.preview_table.column("updated_at", width=150)
        
        self.preview_table["show"] = "headings"
        self.preview_table.pack(fill=BOTH, expand=1)
    
    def preview_export_data(self):
        # Clear existing data
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)
        
        # Get query based on selection
        query = {}
        if self.export_data.get() == "Active Employees":
            query = {"status": "Active"}
        elif self.export_data.get() == "Inactive Employees":
            query = {"status": "Inactive"}
        
        # Fetch data from MongoDB
        data = self.db['employees'].find(query)
        
        # Insert into preview table
        for record in data:
            self.preview_table.insert("", "end", values=(
                record.get("emp_id", ""),
                record.get("name", ""),
                record.get("designation", ""),
                record.get("status", ""),
                record.get("address", ""),
                record.get("email", ""),
                record.get("contact", ""),
                record.get("proof_id", ""),
                record.get("hired_location", ""),
                record.get("doj", ""),
                record.get("dob", ""),
                record.get("age", ""),
                record.get("experience", ""),
                record.get("gender", ""),
                record.get("created_at", ""),
                record.get("updated_at", "")
            ))
    
    def export_data_action(self):
        export_format = self.export_format.get()
        export_data_type = self.export_data.get()
        
        # Get query based on selection
        query = {}
        if export_data_type == "Active Employees":
            query = {"status": "Active"}
        elif export_data_type == "Inactive Employees":
            query = {"status": "Inactive"}
        
        # Fetch data from MongoDB
        data = list(self.db['employees'].find(query))
        
        if not data:
            messagebox.showinfo("Info", "No data to export")
            return
        
        if export_format == "CSV":
            self.export_to_csv(data, export_data_type)
        else:
            self.export_to_pdf(data, export_data_type)
    
    def export_to_csv(self, data, export_data_type):
        try:
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{export_data_type.replace(' ', '_')}.csv"
            )
            
            if not file_path:
                return
            
            # Write data to CSV
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ["emp_id", "name", "designation", "age", "gender", 
                            "experience", "email", "contact", "hired_location",
                            "status", "address", "proof_id", "dob", "doj", "created_at", "updated_at"]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in data:
                    # Remove MongoDB _id field
                    if "_id" in record:
                        del record["_id"]
                    if "created_at" in record:
                        del record["created_at"]
                    if "updated_at" in record:
                        del record["updated_at"]

                    
                    writer.writerow(record)
            
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")
    
    def export_to_pdf(self, data, export_data_type):
        try:
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"{export_data_type.replace(' ', '_')}.pdf"
            )
            
            if not file_path:
                return
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title = Paragraph(f"Employee Data - {export_data_type}", styles['Title'])
            elements.append(title)
            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
            
            # Prepare data for table
            table_data = [["Emp ID", "Name", "Designation", "Status","Email","DOB", "Experience", "Gender"]]
            
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
            
            # Create table
            table = Table(table_data)
            
            # Add style to table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            
            table.setStyle(style)
            elements.append(table)
            
            # Add timestamp
            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
            timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                styles['Normal'])
            elements.append(timestamp)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")
    
    def show_reports_window(self, parent):
        # Clear any existing content in the main area
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        
        # Main content frame
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add back button with square box and color
        back_btn = tk.Button(main_frame, text="←", command=lambda: self.show_dashboard(), 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        # Title
        title_label = tk.Label(main_frame, text="Employee Reports", 
                             font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50")
        title_label.pack(pady=20)
        
        # Reports grid
        reports_frame = tk.Frame(main_frame, bg="#ecf0f1")
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Report cards
        self.create_report_card(reports_frame, "Employee Status Report", 
                              "View distribution of employees by status", 
                              self.show_status_report, 0, 0)
        
        self.create_report_card(reports_frame, "Department Distribution", 
                              "View employees by department/designation", 
                              self.show_department_report, 0, 1)
        
        self.create_report_card(reports_frame, "Experience Analysis", 
                              "View employee experience distribution", 
                              self.show_experience_report, 1, 0)
        
        self.create_report_card(reports_frame, "Location Distribution", 
                              "View employees by hired location", 
                              self.show_location_report, 1, 1)
        
        self.create_report_card(reports_frame, "Age Analysis", 
                              "View employee age distribution", 
                              self.show_age_report, 2, 0)
        
        self.create_report_card(reports_frame, "Gender Distribution", 
                              "View employee gender distribution", 
                              self.show_gender_report, 2, 1)
        
        self.create_report_card(reports_frame, "Salary Analysis", 
                              "View employee salary distribution", 
                              self.show_salary_report, 3, 0)
        
        self.create_report_card(reports_frame, "Proof ID Distribution", 
                              "View employee proof ID distribution",
                              self.show_proof_id_report, 3, 1)
        
        self.create_report_card(reports_frame, "Export Data",
                                "Export employee data to CSV",
                                self.export_data_action, 4, 0)
        
        self.create_report_card(reports_frame, "Exit",
                                "Exit the application",
                                self.exit_action, 4, 1)
    


    def create_report_card(self, parent, title, description, command, row, col):
        card = tk.Frame(parent, bg="white", bd=1, relief=RIDGE, width=300, height=200)
        card.grid(row=row, column=col, padx=20, pady=20)
        card.grid_propagate(False)  # Prevent the frame from shrinking
        
        tk.Label(card, text=title, font=("Arial", 14, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        tk.Label(card, text=description, font=("Arial", 10), 
               bg="white", fg="#7f8c8d", wraplength=250).pack(fill=tk.X, padx=10)
        
        tk.Button(card, text="View Report", command=command, 
                bg="#3498db", fg="white", font=("Arial", 10)).pack(pady=20)
    
    def show_status_report(self):
        # Create a new window for the report
        report_window = tk.Toplevel()
        report_window.title("Employee Status Report")
        report_window.geometry("600x500")
        report_window.configure(bg="#f0f0f0")
         

        # Title
        tk.Label(report_window, text="Employee Status Distribution", 
               font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Get data from MongoDB
        active_count = self.db['employees'].count_documents({"status": "Active"})
        inactive_count = self.db['employees'].count_documents({"status": "Inactive"})
        on_leave_count = self.db['employees'].count_documents({"status": "On Leave"})
        
        # Create a frame for the report
        report_frame = tk.Frame(report_window, bg="white", bd=2, relief=RIDGE)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Display data in a simple format
        tk.Label(report_frame, text=f"Active Employees: {active_count}", 
               font=("Arial", 14), bg="white", fg="#2ecc71", pady=10).pack(fill=tk.X, padx=20)
        
        tk.Label(report_frame, text=f"Inactive Employees: {inactive_count}", 
               font=("Arial", 14), bg="white", fg="#e74c3c", pady=10).pack(fill=tk.X, padx=20)
        
        tk.Label(report_frame, text=f"Employees on Leave: {on_leave_count}", 
               font=("Arial", 14), bg="white", fg="#f39c12", pady=10).pack(fill=tk.X, padx=20)
        
        # Total
        total = active_count + inactive_count + on_leave_count
        tk.Label(report_frame, text=f"Total Employees: {total}", 
               font=("Arial", 14, "bold"), bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X, padx=20)
        
        # Export button
        tk.Button(report_window, text="Export Report", 
                command=lambda: self.export_status_report(active_count, inactive_count, on_leave_count), 
                bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)
    
    def export_status_report(self, active, inactive, on_leave):
        try:
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile="Employee_Status_Report.pdf"
            )
            
            if not file_path:
                return
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title = Paragraph("Employee Status Distribution Report", styles['Title'])
            elements.append(title)
            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
            
            # Prepare data for table
            table_data = [["Status", "Count", "Percentage"]]
            
            total = active + inactive + on_leave
            
            table_data.append(["Active", str(active), f"{(active/total)*100:.2f}%"])
            table_data.append(["Inactive", str(inactive), f"{(inactive/total)*100:.2f}%"])
            table_data.append(["On Leave", str(on_leave), f"{(on_leave/total)*100:.2f}%"])
            table_data.append(["Total", str(total), "100.00%"])
            
            # Create table
            table = Table(table_data)
            
            # Add style to table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Highlight the total row
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ])
            
            table.setStyle(style)
            elements.append(table)
            
            # Add timestamp
            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
            timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                styles['Normal'])
            elements.append(timestamp)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", f"Report exported successfully to {file_path}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting report: {str(e)}")
    
    def show_department_report(self):
        # Create a new window for the report
        report_window = tk.Toplevel()
        report_window.title("Department Distribution Report")
        report_window.geometry("600x500")
        report_window.configure(bg="#f0f0f0")
        
        # Title
        tk.Label(report_window, text="Employee Department Distribution", 
               font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Get data from MongoDB - aggregate by designation
        pipeline = [
            {"$group": {"_id": "$designation", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        department_data = list(self.db['employees'].aggregate(pipeline))
        
        # Create a frame for the report
        report_frame = tk.Frame(report_window, bg="white", bd=2, relief=RIDGE)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create table with scrollbars
        scroll_frame = tk.Frame(report_frame, bg="white")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_y = Scrollbar(scroll_frame, orient=VERTICAL)
        
        dept_table = ttk.Treeview(scroll_frame,
                                columns=("department", "count"),
                                yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_y.config(command=dept_table.yview)
        
        # Configure column headings
        dept_table.heading("department", text="Department/Designation")
        dept_table.heading("count", text="Number of Employees")
        
        # Configure column widths
        dept_table.column("department", width=300)
        dept_table.column("count", width=200)
        
        dept_table["show"] = "headings"
        dept_table.pack(fill=BOTH, expand=1)
        
        # Insert data into table
        total = 0
        for dept in department_data:
            dept_table.insert("", "end", values=(
                dept["_id"] if dept["_id"] else "Not Specified",
                dept["count"]
            ))
            total += dept["count"]
        
        # Display total
        tk.Label(report_window, text=f"Total Employees: {total}", 
               font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=5)
        
        # Export button
        tk.Button(report_window, text="Export Report", 
                command=lambda: self.export_department_report(department_data), 
                bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)
    
    def export_department_report(self, department_data):
        try:
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile="Department_Distribution_Report.pdf"
            )
            
            if not file_path:
                return
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title = Paragraph("Employee Department Distribution Report", styles['Title'])
            elements.append(title)
            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
            
            # Prepare data for table
            table_data = [["Department/Designation", "Count", "Percentage"]]
            
            total = sum(dept["count"] for dept in department_data)
            
            for dept in department_data:
                dept_name = dept["_id"] if dept["_id"] else "Not Specified"
                count = dept["count"]
                percentage = (count/total)*100
                table_data.append([dept_name, str(count), f"{percentage:.2f}%"])
            
            # Add total row
            table_data.append(["Total", str(total), "100.00%"])
            
            # Create table
            table = Table(table_data)
            
            # Add style to table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Highlight the total row
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ])
            
            table.setStyle(style)
            elements.append(table)
            
            # Add timestamp
            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
            timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                styles['Normal'])
            elements.append(timestamp)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", f"Report exported successfully to {file_path}")
            
            # Ask if user wants to open the file
            if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting report: {str(e)}")
      
    def show_experience_report(self):
        # Create a new window for the report
        report_window = tk.Toplevel()
        report_window.title("Experience Profile Analytics")
        report_window.geometry("700x500")
        report_window.configure(bg="#f0f0f0")
        
        # Title
        tk.Label(report_window, text="Employee Experience Distribution Analysis", 
               font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        try:
            # Get all employees from MongoDB
            employees = list(self.db['employees'].find({}, {
                "name": 1, 
                "designation": 1, 
                "experience": 1
            }))
            
            # Create experience categories
            categories = {
                "Less than 1 year": 0,
                "1-3 years": 0,
                "3-5 years": 0,
                "5-10 years": 0,
                "10+ years": 0,
                "Not specified": 0
            }
            
            # Categorize employees
            categorized_employees = {category: [] for category in categories.keys()}
            
            # New approach for experience categorization
            def categorize_experience(employee):
                exp_value = employee.get("experience", "")
                
                # If empty, return "Not specified"
                if not exp_value:
                    return "Not specified"
                
                # Convert to string and clean it
                exp_str = str(exp_value).strip().lower()
                
                # Try different parsing strategies
                
                # Strategy 1: Direct numeric value (e.g., "3", "4.5")
                try:
                    years = float(exp_str)
                    # Categorize based on years
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
                except ValueError:
                    pass
                
                # Strategy 2: Extract first number (e.g., "3 years", "4.5 yrs")
                import re
                number_match = re.search(r'(\d+\.?\d*)', exp_str)
                if number_match:
                    try:
                        years = float(number_match.group(1))
                        # Categorize based on years
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
                    except ValueError:
                        pass
                
                # Strategy 3: Check for range patterns (e.g., "3-5 years")
                range_match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', exp_str)
                if range_match:
                    try:
                        min_years = float(range_match.group(1))
                        max_years = float(range_match.group(2))
                        avg_years = (min_years + max_years) / 2
                        
                        # Categorize based on average years
                        if avg_years < 1:
                            return "Less than 1 year"
                        elif avg_years < 3:
                            return "1-3 years"
                        elif avg_years < 5:
                            return "3-5 years"
                        elif avg_years < 10:
                            return "5-10 years"
                        else:
                            return "10+ years"
                    except ValueError:
                        pass
                
                # Strategy 4: Check for specific keywords
                if "less than 1" in exp_str or "<1" in exp_str:
                    return "Less than 1 year"
                elif any(x in exp_str for x in ["1-3", "1 to 3", "1 - 3"]):
                    return "1-3 years"
                elif any(x in exp_str for x in ["3-5", "3 to 5", "3 - 5"]):
                    return "3-5 years"
                elif any(x in exp_str for x in ["5-10", "5 to 10", "5 - 10"]):
                    return "5-10 years"
                elif "10+" in exp_str or ">10" in exp_str or "more than 10" in exp_str:
                    return "10+ years"
                
                # If all strategies fail, return "Not specified"
                return "Not specified"
            
            # Process all employees
            for emp in employees:
                category = categorize_experience(emp)
                categories[category] += 1
                categorized_employees[category].append(emp)
            
            # Create main container frame
            main_container = tk.Frame(report_window, bg="white", bd=2, relief=RIDGE)
            main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Create left panel for summary
            left_panel = tk.Frame(main_container, bg="white", width=300)
            left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
            left_panel.pack_propagate(False)  # Prevent shrinking
            
            # Create right panel for employee list
            right_panel = tk.Frame(main_container, bg="white")
            right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Summary title
            tk.Label(left_panel, text="Experience Summary", 
                   font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=5)
            
            # Calculate total for percentage
            total_employees = len(employees)
            
            # Create summary table
            summary_frame = tk.Frame(left_panel, bg="white")
            summary_frame.pack(fill=tk.X, pady=5)
            
            # Headers
            tk.Label(summary_frame, text="Experience Range", 
                   font=("Arial", 11, "bold"), bg="#3498db", fg="white").grid(row=0, column=0, sticky="ew", padx=1, pady=1)
            tk.Label(summary_frame, text="Count", 
                   font=("Arial", 11, "bold"), bg="#3498db", fg="white").grid(row=0, column=1, sticky="ew", padx=1, pady=1)
            tk.Label(summary_frame, text="Percentage", 
                   font=("Arial", 11, "bold"), bg="#3498db", fg="white").grid(row=0, column=2, sticky="ew", padx=1, pady=1)
            
            # Fill summary table
            row_idx = 1
            for category, count in categories.items():
                bg_color = "#f9f9f9" if row_idx % 2 == 0 else "white"
                percentage = (count / total_employees) * 100 if total_employees > 0 else 0
                
                tk.Label(summary_frame, text=category, 
                       font=("Arial", 10), bg=bg_color).grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
                tk.Label(summary_frame, text=str(count), 
                       font=("Arial", 10), bg=bg_color).grid(row=row_idx, column=1, padx=5, pady=1)
                tk.Label(summary_frame, text=f"{percentage:.2f}%", 
                       font=("Arial", 10), bg=bg_color).grid(row=row_idx, column=2, padx=5, pady=1)
                
                row_idx += 1
            
            # Total row
            tk.Label(summary_frame, text="Total", 
                   font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
            tk.Label(summary_frame, text=str(total_employees), 
                   font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=row_idx, column=1, padx=5, pady=1)
            tk.Label(summary_frame, text="100.00%", 
                   font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=row_idx, column=2, padx=5, pady=1)
            
            # Right panel title
            tk.Label(right_panel, text="Employee List", 
                   font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=5)
            
            # Create dropdown for selecting experience range
            tk.Label(right_panel, text="Select Experience Range:", 
                   font=("Arial", 11), bg="white").pack(anchor="w", padx=5)
            
            selected_range = tk.StringVar()
            range_dropdown = ttk.Combobox(right_panel, textvariable=selected_range, 
                                        values=list(categories.keys()), state="readonly", width=30)
            range_dropdown.pack(anchor="w", padx=5, pady=5)
            range_dropdown.current(0)  # Set default value
            
            # Create count display label
            employee_count_var = tk.StringVar(value=f"Employees: {categories[list(categories.keys())[0]]}")
            employee_count = tk.Label(right_panel, textvariable=employee_count_var, 
                                    font=("Arial", 11, "bold"), bg="white", fg="#2c3e50")
            employee_count.pack(anchor="w", padx=5, pady=5)
            
            # Create scrollable list for employees
            list_frame = tk.Frame(right_panel, bg="white")
            list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            scroll_y = Scrollbar(list_frame, orient=VERTICAL)
            emp_list = tk.Listbox(list_frame, font=("Arial", 11), height=15,
                                yscrollcommand=scroll_y.set)
            scroll_y.config(command=emp_list.yview)
            
            scroll_y.pack(side=RIGHT, fill=Y)
            emp_list.pack(fill=BOTH, expand=True)
            
            # Function to update employee list when range is selected
            def update_employee_list(*args):
                emp_list.delete(0, tk.END)  # Clear list
                selected = selected_range.get()
                
                if selected:
                    # Get employees in this category
                    emps = categorized_employees[selected]
                    count = len(emps)
                    
                    # Update count display
                    employee_count_var.set(f"Employees: {count}")
                    
                    if count == 0:
                        emp_list.insert(tk.END, "No employees in this category")
                    else:
                        for emp in emps:
                            name = emp.get("name", "Unknown")
                            designation = emp.get("designation", "Unknown")
                            experience = emp.get("experience", "Not specified")
                            
                            emp_list.insert(tk.END, f"{name} - {designation} - {experience}")
            
            # Bind the dropdown to update function
            selected_range.trace("w", update_employee_list)
            
            # Initialize the list with the first category
            update_employee_list()
            
            # Export button
            tk.Button(report_window, text="Export Report", 
                    command=lambda: self.export_simple_experience_report(categories, categorized_employees, total_employees), 
                    bg="#3498db", fg="white", font=("Arial", 12)).pack(pady=10)
            
        except Exception as e:
            # If there's an error, show error message
            tk.Label(report_window, text=f"Error generating report: {str(e)}", 
                   font=("Arial", 12), bg="#f0f0f0", fg="#e74c3c", pady=10).pack(fill=tk.X)
            print(f"Error in experience report: {str(e)}")

    def export_simple_experience_report(self, categories, categorized_employees, total_employees):
            try:
                # Ask for file location
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", ".pdf"), ("CSV files", ".csv")],
                    initialfile="Employee_Experience_Analysis.pdf"
                )
                
                if not file_path:
                    return
                
                # Determine export format based on file extension
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext == '.csv':
                    # Export to CSV
                    with open(file_path, 'w', newline='') as csvfile:
                        # Create CSV writer
                        writer = csv.writer(csvfile)
                        
                        # Write header
                        writer.writerow(["Experience Range", "Number of Employees", "Percentage", "Employee Names"])
                        
                        # Write data for each category
                        for category, count in categories.items():
                            percentage = (count / total_employees) * 100 if total_employees > 0 else 0
                            
                            # Get employee names in this category
                            employee_names = [emp.get("name", "Unknown") for emp in categorized_employees[category]]
                            names_str = ", ".join(employee_names)
                            
                            writer.writerow([category, count, f"{percentage:.2f}%", names_str])
                        
                        # Write total row
                        writer.writerow(["Total", total_employees, "100.00%", ""])
                    
                    messagebox.showinfo("Success", f"Report exported successfully to {file_path}")
                    
                else:  # PDF export
                    # Create PDF document
                    doc = SimpleDocTemplate(file_path, pagesize=letter)
                    elements = []
                    
                    # Add title
                    styles = getSampleStyleSheet()
                    title = Paragraph("Employee Experience Distribution Analysis", styles['Title'])
                    elements.append(title)
                    elements.append(Paragraph(" ", styles['Normal']))  # Add some space
                    
                    # Add summary text
                    summary_text = Paragraph("This report provides an analysis of employee experience distribution across the organization.", styles['Normal'])
                    elements.append(summary_text)
                    elements.append(Paragraph(" ", styles['Normal']))  # Add some space
                    
                    # Prepare data for summary table
                    table_data = [["Experience Range", "Number of Employees", "Percentage"]]
                    
                    for category, count in categories.items():
                        percentage = (count / total_employees) * 100 if total_employees > 0 else 0
                        table_data.append([
                            category,
                            str(count),
                            f"{percentage:.2f}%"
                        ])
                    
                    # Add total row
                    table_data.append(["Total", str(total_employees), "100.00%"])
                    
                    # Create table
                    table = Table(table_data)
                    
                    # Add style to table
                    style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        # Highlight the total row
                        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ])
                    
                    table.setStyle(style)
                    elements.append(table)
                    
                    # Add detailed employee lists for each category
                    elements.append(Paragraph(" ", styles['Normal']))  # Add some space
                    elements.append(Paragraph("Detailed Employee Lists by Experience Category", styles['Heading2']))
                    
                    for category, employees in categorized_employees.items():
                        if employees:  # Only add categories with employees
                            elements.append(Paragraph(" ", styles['Normal']))  # Add some space
                            elements.append(Paragraph(f"{category} ({len(employees)} employees)", styles['Heading3']))
                            
                            # Create employee list
                            employee_data = [["Name", "Designation", "Experience"]]
                            
                            for emp in employees:
                                employee_data.append([
                                    emp.get("name", "Unknown"),
                                    emp.get("designation", "Unknown"),
                                    str(emp.get("experience", "Not specified"))
                                ])
                            
                            # Create employee table
                            emp_table = Table(employee_data)
                            
                            # Add style to employee table
                            emp_style = TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                            ])
                            
                            emp_table.setStyle(emp_style)
                            elements.append(emp_table)
                    
                    # Add timestamp
                    elements.append(Paragraph(" ", styles['Normal']))  # Add some space
                    timestamp = Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                        styles['Normal'])
                    elements.append(timestamp)
                    
                    # Build PDF
                    doc.build(elements)
                    
                    messagebox.showinfo("Success", f"Report exported successfully to {file_path}")
                
                # Ask if user wants to open the file
                if messagebox.askyesno("Open File", "Do you want to open the exported file?"):
                    os.startfile(file_path)
                        
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting report: {str(e)}")
        


    def show_location_report(self):
        # Placeholder for location report
        messagebox.showinfo("Coming Soon", "Location Distribution Report is under development")
    
    def show_settings_window(self, parent):
        # Clear any existing content in the main area
        for widget in parent.winfo_children():
            if widget.winfo_class() != "Frame" or widget.cget("bg") != "#2c3e50":
                widget.destroy()
        
        # Main content frame
        main_frame = tk.Frame(parent, bg="#82abca")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add back button with square box and color
        back_btn = tk.Button(main_frame, text="←", command=lambda: self. show_dashboard(), 
                       font=("Impact", 18, "bold"), bg="#e2f6fd", fg="#000000", bd=0)
        back_btn.place(x=5, y=5)

        # Title
        title_label = tk.Label(main_frame, text="Settings", 
                             font=("Arial", 20, "bold"), bg="#82abca", fg="#2c3e50")
        title_label.pack(pady=20)
        
        # Settings frame
        settings_frame = tk.Frame(main_frame, bg="white", bd=2, relief=RIDGE)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Settings title
        tk.Label(settings_frame, text="Application Settings", font=("Arial", 16, "bold"), 
               bg="white", fg="#2c3e50", pady=10).pack(fill=tk.X)
        
        # Settings options
        options_frame = tk.Frame(settings_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Database settings
        tk.Label(options_frame, text="Database Settings", font=("Arial", 14, "bold"), 
               bg="white", fg="#2c3e50").grid(row=0, column=0, sticky="w", pady=10, columnspan=2)
        
        tk.Label(options_frame, text="MongoDB Connection String:", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=1, column=0, sticky="w", pady=5)
        
        self.connection_string = StringVar(value="db_url")
        tk.Entry(options_frame, textvariable=self.connection_string, font=("Arial", 12), 
                bg="#f0f0f0", width=30).grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # User settings
        tk.Label(options_frame, text="User Settings", font=("Arial", 14, "bold"), 
               bg="white", fg="#2c3e50").grid(row=2, column=0, sticky="w", pady=10, columnspan=2)
        
        tk.Label(options_frame, text="Change Password", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=3, column=0, sticky="w", pady=5)
        
        tk.Button(options_frame, text="Change Password", command=self.show_change_password, 
                bg="#3498db", fg="white", font=("Arial", 10)).grid(row=3, column=1, pady=5, padx=5, sticky="w")
        
        # Application settings
        tk.Label(options_frame, text="Application Settings", font=("Arial", 14, "bold"), 
               bg="white", fg="#2c3e50").grid(row=4, column=0, sticky="w", pady=10, columnspan=2)
        
        # Theme selection
        tk.Label(options_frame, text="Theme:", font=("Arial", 12), 
               bg="white", fg="#2c3e50").grid(row=5, column=0, sticky="w", pady=5)
        
        self.theme = StringVar(value="Light")
        theme_combo = ttk.Combobox(options_frame, textvariable=self.theme, 
                                 font=("Arial", 12), state="readonly", values=("Light", "Dark"))
        theme_combo.grid(row=5, column=1, pady=5, padx=5, sticky="w")
        
        # Save settings button
        tk.Button(settings_frame, text="Save Settings", command=self.save_settings, 
                bg="#2ecc71", fg="white", font=("Arial", 12), width=15).pack(pady=20)
    
    def show_change_password(self):
        # Create a new window for changing password
        password_window = tk.Toplevel()
        password_window.title("Change Password")
        password_window.geometry("400x300")
        password_window.configure(bg="#f0f0f0")
        
        # Create a frame for the form
        frame = tk.Frame(password_window, bg="#f0f0f0")
        frame.pack(expand=True)
        
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
            
            # Verify current password from MongoDB
            user = users_collection.find_one({"username": "current_user"})  # Replace with actual username
            
            if user and bcrypt.checkpw(current_password.get().encode('utf-8'), user['password']):
                # Update password
                hashed_password = bcrypt.hashpw(new_password.get().encode('utf-8'), bcrypt.gensalt())
                users_collection.update_one(
                    {"username": "current_user"},  # Replace with actual username
                    {"$set": {"password": hashed_password}}
                )
                messagebox.showinfo("Success", "Password changed successfully")
                password_window.destroy()
            else:
                messagebox.showerror("Error", "Current password is incorrect")
        
        tk.Button(frame, text="Change Password", command=change_password_action,
                 bg="#3498db", fg="white", font=("Arial", 12), width=15).grid(row=3, column=0, columnspan=2, pady=20)
    
    def save_settings(self):
        # Save connection string
        connection_string = self.connection_string.get()
        
        # Save theme preference
        theme = self.theme.get()
        
        # Here you would typically save these settings to a config file or database
        # For now, just show a success message
        messagebox.showinfo("Success", "Settings saved successfully")
        
        # Apply theme if changed
        if theme == "Dark":
            # Apply dark theme
            self.root.configure(bg="#2c3e50")
        else:
            # Apply light theme
            self.root.configure(bg="#f0f0f0")

if __name__ == "__main__":
      root = tk.Tk()
      app = AuthenticationApp(root)
      root.mainloop()        