from django import forms
from django.core.exceptions import ValidationError
from .models import PerformanceRecord
from employee.models import Employee
import datetime

class PerformanceRecordForm(forms.ModelForm):
    class Meta:
        model = PerformanceRecord
        fields = ['employee', 'year', 'month', 'task_completion_percentage', 'project_rating']
        widgets = {
            'employee': forms.Select(attrs={'class': 'role-select'}),
            'year': forms.Select(attrs={'class': 'role-select'}),
            'month': forms.Select(attrs={'class': 'role-select'}),
            'task_completion_percentage': forms.NumberInput(attrs={'class': 'role-select', 'min': '0.0', 'max': '100.0', 'step': '0.1', 'placeholder': 'Enter task completion %...'}),
            'project_rating': forms.NumberInput(attrs={'class': 'role-select', 'min': '0.0', 'max': '5.0', 'step': '0.1', 'placeholder': 'Enter rating (0.0 - 5.0)...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate year and month options dynamically
        today = datetime.date.today()
        year_choices = [(y, y) for y in range(today.year - 5, today.year + 2)]
        month_choices = [(m, datetime.date(2000, m, 1).strftime('%B')) for m in range(1, 13)]
        
        self.fields['year'].widget.choices = year_choices
        self.fields['month'].widget.choices = month_choices

    def clean_task_completion_percentage(self):
        val = self.cleaned_data.get('task_completion_percentage')
        if val is not None and (val < 0.0 or val > 100.0):
            raise ValidationError("Task completion percentage must be between 0.0 and 100.0.")
        return val

    def clean_project_rating(self):
        val = self.cleaned_data.get('project_rating')
        if val is not None and (val < 0.0 or val > 5.0):
            raise ValidationError("Project rating must be between 0.0 and 5.0.")
        return val
