from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee')
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.CharField(max_length=15)
    department=models.CharField(max_length=100)
    designation=models.CharField(max_length=100)
    salary=models.FloatField()
    role=models.CharField(max_length=20, choices=[('Admin', 'Admin'), ('Employee', 'Employee')], default='Employee')

    def __str__(self):
        return self.name