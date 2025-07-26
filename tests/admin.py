from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import TestCategory, TestType, Test, TestResult

@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description']
    search_fields = ['name', 'code']

@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'sample_type', 'cost']
    list_filter = ['category', 'sample_type', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'patient', 'test_type', 'status', 'priority', 'ordered_date']
    list_filter = ['status', 'priority', 'test_type__category']
    search_fields = ['test_id', 'patient__first_name', 'patient__last_name']

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test', 'result_value', 'is_abnormal', 'reviewed_by', 'created_date']
    list_filter = ['is_abnormal', 'reviewed_by']
