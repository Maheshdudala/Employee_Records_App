from dataclasses import dataclass, asdict
from .models import Employee
from django.db import transaction, IntegrityError
import logging
from .models import Employee


@dataclass
class EmployeeRecord:
    employee_id: int
    name: str
    email: str
    department: str
    designation: str
    salary: float
    date_of_joining: str  # YYYY-MM-DD format

    def to_model(self):
        return Employee(**asdict(self))


logging.basicConfig(level=logging.INFO)


def bulk_insert_employees(employee_list, batch_size=500):
    """Bulk insert employee records into the database with batch processing."""
    skipped_records = []
    try:
        with transaction.atomic():
            for i in range(0, len(employee_list), batch_size):
                batch = employee_list[i: i + batch_size]
                Employee.objects.bulk_create(batch, batch_size=batch_size, ignore_conflicts=False)

        logging.info(f"Bulk insert successful. {len(employee_list)} records added.")
        if skipped_records:
            logging.warning(f"Skipped {len(skipped_records)} records: {skipped_records}")

        return {"message": f"Bulk insert successful. {len(employee_list)} records added."}
    except IntegrityError as e:
        logging.error(f"Error during bulk insert: {str(e)}")
        return {"error": "Database integrity issue."}



