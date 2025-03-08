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
