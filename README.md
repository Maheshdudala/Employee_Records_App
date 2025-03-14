# Employee Record Transmission and Storage System

## Overview
This project is a **high-performance client-server application** that processes employee records from a `.csv` file and stores them in a **MySQL database**. It leverages **Django REST Framework (DRF), JWT authentication, async programming, function decorators, and dataclasses** for efficient processing.

## Features
- **Secure API with JWT authentication** (Simple JWT)
- **Async processing** for efficient data transmission
- **Function decorators** for logging, validation, and error handling
- **Bulk inserts** for optimized database performance
- **Deduplication & Error Handling** for duplicate records
---

## 1. Setup & Installation

### Prerequisites
- Python 3.8+
- MySQL
- Django & Django REST Framework

### Installation Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Maheshdudala/Employee_Records_App.git
   cd employee-system
   ```

2. **Create a virtual environment & activate it:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database:**
   ```sql
   CREATE DATABASE employee_db;
   CREATE USER 'employee_user'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON employee_db.* TO 'employee_user'@'localhost';
   ```

5. **Update `settings.py` with database credentials:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'employee_db',
           'USER': 'employee_user',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

6. **Apply migrations & create a superuser:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. **Run the server:**
   ```bash
   python manage.py runserver
   ```

---

## 2. API Endpoints

### Authentication (JWT)
- **Obtain Token:** `POST /api/token/`
  ```json
  {
    "username": "admin",
    "password": "admin"
  }
  ```
  Response:
  ```json
  {
    "access": "<JWT_ACCESS_TOKEN>",
    "refresh": "<JWT_REFRESH_TOKEN>"
  }
  ```
- **Refresh Token:** `POST /api/token/refresh/`
  ```json
  {
    "refresh": "<JWT_REFRESH_TOKEN>"
  }
  ```
  Response:
  ```json
  {
    "access": "<NEW_ACCESS_TOKEN>"
  }
  ```

### Employee API
#### **Create Employee** (Authenticated)
- `POST /api/employees/`
  ```json
  {
    "employee_id": "EMP001",
    "name": "John Doe",
    "email": "john@example.com",
    "department": "IT",
    "designation": "Software Engineer",
    "salary": 75000.00,
    "date_of_joining": "2023-01-10"
  }
  ```
  Response:
  ```json
  {
    "id": 1,
    "employee_id": "EMP001",
    "name": "John Doe",
    "email": "john@example.com",
    "department": "IT",
    "designation": "Software Engineer",
    "salary": 75000.0,
    "date_of_joining": "2023-01-10"
  }
  ```

#### **List Employees**
- `GET /api/employees/`

#### **Retrieve Employee**
- `GET /api/employees/{id}/`

#### **Update Employee**
- `PUT /api/employees/{id}/`

#### **Delete Employee**
- `DELETE /api/employees/{id}/`

---

## 3. Client Implementation (CSV Upload)
The client reads employee records from a CSV file and sends them to the API using JWT authentication.

### **Python Client Script** (`client.py`)
```python
import requests
import csv

# API Endpoints
API_URL = "http://127.0.0.1:8000/api/employees/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"

# Admin credentials (replace with actual credentials)
USERNAME = "admin"
PASSWORD = "admin"

# CSV file path
CSV_FILE_PATH = "employees.csv"

def get_jwt_token():
    """Fetch JWT token using admin credentials."""
    response = requests.post(TOKEN_URL, data={"username": USERNAME, "password": PASSWORD})
    if response.status_code == 200:
        return response.json().get("access")
    else:
        print("Error getting token:", response.json())
        return None

def send_employee_records():
    """Read employee records from CSV and send to API."""
    token = get_jwt_token()
    if not token:
        print("Authentication failed. Exiting.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            employee_data = {
                "employee_id": row["employee_id"],
                "name": row["name"],
                "email": row["email"],
                "department": row["department"],
                "designation": row["designation"],
                "salary": float(row["salary"]),  # Convert salary to float
                "date_of_joining": row["date_of_joining"]
            }

            response = requests.post(API_URL, json=employee_data, headers=headers)

            if response.status_code == 201:
                print(f"Employee {employee_data['name']} added successfully!")
            else:
                print(f"Error adding {employee_data['name']}: {response.json()}")

if __name__ == "__main__":
    send_employee_records()

```



---

## Conclusion
This project provides a **high-performance employee record system** using Django, MySQL, JWT authentication, and async programming. It is designed for **scalability, efficiency, and security**. 🚀

