from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import ReportTemplate, Report

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'created_date']
    list_filter = ['is_default']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'patient', 'status', 'report_format', 'generated_date']
    list_filter = ['status', 'report_format', 'is_confidential']
    search_fields = ['report_id', 'patient__first_name', 'patient__last_name']

