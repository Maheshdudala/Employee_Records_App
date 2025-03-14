
import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Employee
from .serializers import EmployeeSerializer
from .decorators import log_execution_time, validate_input, handle_exceptions
from .utils import bulk_insert_employees, EmployeeRecord
from django.db import transaction, IntegrityError


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    @log_execution_time
    @validate_input
    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """Handles both single and bulk employee creation"""
        data = request.data

        # Handle Bulk Insert
        if isinstance(data, list):
            employee_instances = []
            existing_records = Employee.objects.filter(
                Q(email__in=[emp["email"] for emp in data]) |
                Q(employee_id__in=[emp["employee_id"] for emp in data])
            ).values_list("email", "employee_id")

            existing_emails, existing_ids = zip(*existing_records) if existing_records else (set(), set())
            skipped_records = []
            for emp in data:
                if emp["email"] in existing_emails or emp["employee_id"] in existing_ids:
                    skipped_records.append(emp)
                    continue  # Skip duplicates

                # Convert dictionary to EmployeeRecord instance
                emp_record = EmployeeRecord(**emp)
                employee_instances.append(emp_record.to_model())  # Convert to Django model
            if skipped_records:
                logging.warning(f"Skipped {len(skipped_records)} duplicate records: {skipped_records}")

            if not employee_instances:
                return Response({"message": "No new employees to insert."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                try:
                    result = bulk_insert_employees(employee_instances)

                    if "error" in result:
                        return Response(
                            {"message": "❌ Bulk insert failed.", "error": result["error"]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                    return Response(
                        {
                            "message": f"✅ Inserted {len(employee_instances) - result.get('skipped', 0)} employees successfully.",
                            "skipped": result.get("skipped", 0)},
                        status=status.HTTP_201_CREATED
                    )

                except IntegrityError as e:
                    return Response(
                        {"message": "❌ Database integrity issue.", "error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                except Exception as e:
                    return Response(
                        {"message": "❌ An unexpected error occurred.", "error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # return Response({"message": f"Inserted {len(employee_instances)} employees successfully."}, status=status.HTTP_201_CREATED)

        # Handle Single Record
        return super().create(request, *args, **kwargs)

