from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'role-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'search-input'}),
            'status': forms.Select(attrs={'class': 'role-select'}),
        }
