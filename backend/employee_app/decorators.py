import time
import logging
import asyncio
from functools import wraps
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, transaction
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from .models import Employee  # Import your Employee model

logging.basicConfig(level=logging.INFO)

def log_execution_time(func):
    """Decorator to log execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logging.info(f"{func.__name__} executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper

def validate_input(func):
    """Decorator to validate input data."""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return wrapper

from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

def handle_exceptions(func):
    """Decorator to handle errors like duplicate records and database failures."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            logging.error(f"Database Integrity Error: {str(e)}")
            return Response({"error": "Duplicate record detected."}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logging.error(f"Validation Error: {e.message_dict}")
            return Response({"error": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except DRFValidationError as e:
            logging.error(f"DRF Validation Error: {e.detail}")
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Unexpected Error: {str(e)}")
            return Response({"error": "Internal Server Error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


@dataclass
class EmployeeRecord:
    employee_id: int
    name: str
    email: str
    department: str
    designation: str
    salary: float
    date_of_joining: str  # YYYY-MM-DD format

@log_execution_time
@handle_exceptions
def bulk_insert_employees(employee_list):
    """Bulk insert employee records into the database."""
    try:
        with transaction.atomic():
            Employee.objects.bulk_create(employee_list, ignore_conflicts=True)
        return {"message": "Bulk insert successful."}
    except IntegrityError as e:
        logging.error(f"Error during bulk insert: {str(e)}")
        return {"error": "Database integrity issue."}

async def process_csv_async(csv_records):
    """Process CSV records asynchronously."""
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, bulk_insert_employees, csv_records)
        ]
        results = await asyncio.gather(*tasks)
        return results
