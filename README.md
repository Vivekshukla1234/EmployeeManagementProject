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
