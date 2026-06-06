from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Employee

class EmployeeLoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=[('Admin', 'Admin'), ('Employee', 'Employee')],
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        initial='Employee',
        label="Log in as"
    )

class EmployeeAddForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter login username'}),
        help_text="Required for login credentials"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter login password'}),
        help_text="Required for login credentials"
    )

    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'department', 'designation', 'salary', 'role']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
            'department': forms.TextInput(attrs={'placeholder': 'Enter department name'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Enter job title'}),
            'salary': forms.NumberInput(attrs={'placeholder': 'Enter monthly salary'}),
            'role': forms.Select(attrs={'class': 'role-select'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'department', 'designation', 'salary', 'role']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
            'department': forms.TextInput(attrs={'placeholder': 'Enter department name'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Enter job title'}),
            'salary': forms.NumberInput(attrs={'placeholder': 'Enter monthly salary'}),
            'role': forms.Select(attrs={'class': 'role-select'}),
        }
