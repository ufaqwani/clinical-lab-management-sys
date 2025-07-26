from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'gender', 'phone_number', 'created_date']
    list_filter = ['gender', 'blood_group', 'is_active']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['created_date', 'updated_date']
