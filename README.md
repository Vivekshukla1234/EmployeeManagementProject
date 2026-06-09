# Enterprise Employee Management & Attendance System

An enterprise-grade Employee Management and Attendance System built with Django, styled with premium glassmorphic dark-theme aesthetics (Vanilla CSS), featuring Chart.js visual analytics, and an integrated scikit-learn AI model for appraisal grading.

---

## 🚀 Portability & Quick Setup

This project is pre-configured to run out of the box on **any computer** using either **SQLite** (default for easy setup) or **MySQL**.

### Prerequisites
- Python 3.10+
- pip (Python package installer)

### Step 1: Clone and Create Virtual Environment
Open your terminal in the project folder and run:
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Database & Environment Configuration (`.env`)
By default, the project will automatically create and use an SQLite database (`db.sqlite3`), requiring zero external database setup.

To configure the project to use a **MySQL database**, copy `.env.example` to `.env` and adjust the variables:
```ini
DB_ENGINE=mysql
DB_NAME=employeeManagement
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 4: Run Database Migrations
Create the database tables:
```bash
python manage.py migrate
```

### Step 5: Start the Development Server

#### Running on Localhost (Default)
```bash
python manage.py runserver
```
*Accessible at http://127.0.0.1:8000/*

#### Running on a Specific IP Address
To make the application accessible to other computers on the same Local Area Network (LAN), bind the server to your computer's local IP address or `0.0.0.0` (binds to all network interfaces):
```bash
python manage.py runserver 0.0.0.0:8000
```
*To find your computer's local IP address, run `ipconfig` (Windows) or `ifconfig` (macOS/Linux). For example, if your IP is `192.168.1.100`, you can access it from other devices at `http://192.168.1.100:8000/`.*

---

## 🧪 Running the Automated Test Suite

To run all unit and integration tests:
```bash
python manage.py test --noinput
```

---

## 🛠️ Key Credentials

To create an administrator account to access the control panel:
```bash
python manage.py createsuperuser
```
Follow the prompts to set up the username, email, and password.

# AI Powered Employee Management and Attendance System

## Project Overview

The AI Powered Employee Management and Attendance System is a web-based application developed using Django and Python. The system is designed to automate employee management activities such as employee record maintenance, attendance tracking, leave management, performance evaluation, and reporting.

The project integrates Artificial Intelligence concepts for employee appraisal grading and performance assessment, making workforce management more efficient, accurate, and data-driven.

---

## Objectives

* To automate employee management processes.
* To maintain centralized employee records.
* To manage attendance efficiently.
* To simplify leave application and approval processes.
* To generate reports automatically.
* To implement AI-based appraisal grading for employee evaluation.

---

## Key Features

### Employee Management

* Add Employee
* Update Employee
* Delete Employee
* Search Employee
* View Employee Details

### Attendance Management

* Record Attendance
* Attendance Monitoring
* Attendance Reports
* Attendance Analysis

### Leave Management

* Apply Leave
* Approve/Reject Leave Requests
* Leave History Management

### Authentication & Security

* Secure Login System
* Role-Based Access Control
* Session Management

### AI-Based Appraisal System

* Employee Performance Evaluation
* Appraisal Grading
* Data-Driven Decision Support

### Reporting

* Employee Reports
* Attendance Reports
* Leave Reports
* Performance Reports

---

## Technology Stack

### Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

### Backend

* Python
* Django Framework

### Database

* SQLite / MySQL

### AI & Data Processing

* Python Libraries
* Machine Learning Concepts

---

## System Modules

1. Employee Management Module
2. Attendance Management Module
3. Leave Management Module
4. Authentication Module
5. Reporting Module
6. AI-Based Appraisal Grading Module

---

## Installation Steps

### Step 1

Clone the Repository

```bash
git clone https://github.com/Vivekshukla1234/EmployeeManagementProject.git
```

### Step 2

Navigate to Project Directory

```bash
cd EmployeeManagementProject
```

### Step 3

Create Virtual Environment

```bash
python -m venv venv
```

### Step 4

Activate Virtual Environment

```bash
venv\Scripts\activate
```

### Step 5

Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6

Run Migrations

```bash
python manage.py migrate
```

### Step 7

Start Development Server

```bash
python manage.py runserver
```

### Step 8

Open Browser

```text
http://127.0.0.1:8000/
```

---

## Project Documentation

The complete MCA Project Report is included in this repository.

The report contains:

* Abstract
* Extended Abstract
* Literature Review
* Research Methodology
* System Design
* Implementation Details
* Testing and Validation
* Results and Findings
* Future Scope
* Conclusion

---

## Future Enhancements

* Biometric Attendance Integration
* Mobile Application Support
* Cloud Deployment
* Advanced AI Analytics
* Payroll Integration
* Real-Time Dashboards

---

## Author

**Vivek Shukla**

Master of Computer Applications (MCA)

---

## License

This project is developed for academic and educational purposes.
