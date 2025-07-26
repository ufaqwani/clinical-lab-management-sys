from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient

class TestCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        verbose_name_plural = "Test Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TestType(models.Model):
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    sample_type = models.CharField(max_length=50)  # Blood, Urine, etc.
    reference_range = models.CharField(max_length=200, blank=True)
    units = models.CharField(max_length=20, blank=True)
    normal_turnaround_time = models.IntegerField(help_text="Hours")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Test(models.Model):
    STATUS_CHOICES = [
        ('ORDERED', 'Ordered'),
        ('COLLECTED', 'Sample Collected'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('STAT', 'STAT'),
    ]
    
    # Identifiers
    test_id = models.CharField(max_length=20, unique=True, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    
    # Ordering Information
    ordered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordered_tests')
    ordered_date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='ROUTINE')
    
    # Sample Information
    sample_collected_date = models.DateTimeField(null=True, blank=True)
    sample_collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_samples')
    
    # Processing Information
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_tests')
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ORDERED')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-ordered_date']
    
    def __str__(self):
        return f"{self.test_id} - {self.patient.full_name} - {self.test_type.name}"

class TestResult(models.Model):
    test = models.OneToOneField(Test, on_delete=models.CASCADE, related_name='result')
    result_value = models.CharField(max_length=500)
    is_abnormal = models.BooleanField(default=False)
    technician_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result for {self.test.test_id}"
