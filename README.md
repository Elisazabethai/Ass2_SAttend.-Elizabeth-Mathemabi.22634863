Student & Course Management System

A Python-based Student and Course Management System built using Tkinter for the GUI, SQLite3 for the database, and a modular MVC architecture for maintainability.  
This application allows users to register students, manage courses, update or delete records, search, and view/export logs.  
It also supports Light/Dark theme switching, making the UI modern and user-friendly.

Project Structure

project\
├── main.py					# Entry point for the application
├── config.json				# Configuration file (theme settings, colors)
├── db.py					# Database connection 
├── README.md				# Database connection │
│
├── controller/				# (Optional) Future expansion for 
│   ├── init.py
│   ├── course_controller.py	# Controllers methods
│   └── student_controller.py	# Student methods
│
├── data/					# (Optional) Future expansion for controllers
│   └── init.py
├── logs/					# Generated logs (if any)
│
├── model/					# Database Models
│   ├── init.py
│   ├── course_model.py			# Helper methods
│   └── student_model.py		# Student methods
│
└── view/                    # GUI Views
    ├── init.py
    ├── base_view.py			# Base class with theme and styling
    ├── student_view.py			# Student management UI
    └── course_view.py			# Course management UI
								

Features

Student Management – Add, update, delete, and search students  
Course Management – Manage available courses dynamically  
Light/Dark Mode – Toggle UI themes in real-time  
View & Export Logs – Export data to CSV or view in a separate window  
Professional UI – Modern, Discord-inspired design  
MVC Architecture – Clean separation of concerns for easy maintenance  


Install Dependencies

Ensure you have Python 3.10+ installed.
Install required packages (if any):

Run the Application

```bash
python main.py
```

Testing

A Test Plan is required to verify functionality, usability, and performance.

Test cases
Expected results
Pass/Fail tracking
Notes for discovered defects and resolutions

License

This project is licensed under the MIT License – feel free to use and modify for educational purposes.

Author

Developed by Tony O'Shea
Contact: t.oshea@curtin.edu.au

