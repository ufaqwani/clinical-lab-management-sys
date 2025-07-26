from django import forms
from .models import Patient
from django.core.exceptions import ValidationError
import re

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'patient_id', 'first_name', 'last_name', 'date_of_birth', 
            'gender', 'phone_number', 'email', 'address', 'blood_group', 
            'insurance_number', 'emergency_contact'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'patient_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PAT001'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'patient@email.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., O+'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name and phone number'}),
        }

    def clean_patient_id(self):
        patient_id = self.cleaned_data['patient_id']
        if not re.match(r'^PAT\d{3,}$', patient_id):
            raise ValidationError("Patient ID must start with 'PAT' followed by at least 3 digits (e.g., PAT001)")
        return patient_id.upper()

class PatientSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Search by patient ID, name, or phone...'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Patient.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    blood_group = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Blood group'})
    )
