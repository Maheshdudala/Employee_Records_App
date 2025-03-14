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
import asyncio
import aiohttp
import pandas as pd
import logging
from aiohttp import ClientSession
import threading

# API Endpoints
API_URL = "http://127.0.0.1:8000/api/employees/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"

# Admin credentials (replace with actual credentials)
USERNAME = "admin"
PASSWORD = "admin"

# CSV file path
CSV_FILE_PATH = "employees.csv"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Batch size for sending records in chunks
BATCH_SIZE = 500
MAX_RETRIES = 3  # Maximum retry attempts for failed requests


async def get_auth_token():
    """Fetch JWT token using admin credentials."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                TOKEN_URL,
                json={"username": USERNAME, "password": PASSWORD},
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("access")  # Get access token
                else:
                    logging.error(f"❌ Authentication failed! Status: {response.status}, Response: {await response.text()}")
                    return None
        except aiohttp.ClientError as e:
            logging.error(f"❌ Error during authentication: {e}")
            return None


async def send_batch(session: ClientSession, batch: list, auth_token: str):
    """Send a batch of employee records asynchronously."""
    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(API_URL, json=batch, headers=headers) as response:
                if response.status == 201:
                    logging.info(f"✅ Successfully uploaded {len(batch)} records.")
                    return True
                else:
                    logging.error(f"⚠️ Failed to upload. Status: {response.status}, Response: {await response.text()}")
        except aiohttp.ClientError as e:
            logging.error(f"❌ Request failed: {e}")

        logging.info(f"🔄 Retrying batch ({attempt + 1}/{MAX_RETRIES})...")
        await asyncio.sleep(2)  # Wait before retrying

    logging.error(f"❌ Failed after {MAX_RETRIES} retries.")
    return False


async def process_csv(file_path: str):
    """Read CSV and process employee records in bulk."""
    auth_token = await get_auth_token()
    if not auth_token:
        logging.error("❌ Exiting due to authentication failure.")
        return

    df = pd.read_csv(file_path)
    employee_records = df.to_dict(orient="records")


    async with aiohttp.ClientSession() as session:

        tasks = []
        for i in range(0, len(employee_records), BATCH_SIZE):
            batch = employee_records[i : i + BATCH_SIZE]
            tasks.append(send_batch(session, batch, auth_token))

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(process_csv(CSV_FILE_PATH))

```



---

## Conclusion
This project provides a **high-performance employee record system** using Django, MySQL, JWT authentication, and async programming. It is designed for **scalability, efficiency, and security**. 🚀

