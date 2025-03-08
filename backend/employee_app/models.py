from django.db import models

class Employee(models.Model):
    employee_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_joining = models.DateField()

    def __str__(self):
        return self.name
