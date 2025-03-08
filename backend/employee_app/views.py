from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, transaction
from django.db.models import Q
from .models import Employee
from .serializers import EmployeeSerializer
from .decorators import log_execution_time, validate_input, handle_exceptions
from dataclasses import asdict

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

        # Check if the request contains multiple employee records
        if isinstance(data, list):
            employee_instances = []
            existing_emails = set(Employee.objects.filter(email__in=[emp["email"] for emp in data]).values_list("email", flat=True))
            existing_ids = set(Employee.objects.filter(employee_id__in=[emp["employee_id"] for emp in data]).values_list("employee_id", flat=True))

            for emp in data:
                if emp["email"] in existing_emails or emp["employee_id"] in existing_ids:
                    continue  # Skip duplicates

                employee_instances.append(Employee(**emp))  # Convert dict to Employee model instance

            if not employee_instances:
                return Response({"message": "No new employees to insert."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                Employee.objects.bulk_create(employee_instances, ignore_conflicts=True)

            return Response({"message": f"Inserted {len(employee_instances)} employees successfully."}, status=status.HTTP_201_CREATED)

        # Handle Single Record
        return super().create(request, *args, **kwargs)
