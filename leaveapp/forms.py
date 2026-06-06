from django import forms
from django.core.exceptions import ValidationError
from .models import LeaveRequest
import datetime

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'role-select'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'role-select'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'role-select', 'placeholder': 'Provide reason for leave...'}),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date cannot be after end date.")
            
            # Check for overlapping leave requests for the same employee
            if self.employee:
                overlapping_requests = LeaveRequest.objects.filter(
                    employee=self.employee,
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).exclude(status='Rejected')
                
                if self.instance and self.instance.pk:
                    overlapping_requests = overlapping_requests.exclude(pk=self.instance.pk)
                    
                if overlapping_requests.exists():
                    raise ValidationError("You have an overlapping leave request during this period.")
                    
        return cleaned_data
