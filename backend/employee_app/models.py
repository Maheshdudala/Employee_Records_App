from django.db import models

class Employee(models.Model):
    employee_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    salary = models.FloatField()
    date_of_joining = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.employee_id})"
