from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from tests.models import Test
from django.core.files.base import ContentFile
import uuid
from datetime import datetime

class ReportTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, default='standard')
    header_logo = models.ImageField(upload_to='report_templates/logos/', blank=True, null=True)
    footer_text = models.TextField(blank=True, default="This report is electronically generated and signed.")
    is_default = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Report(models.Model):
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('HTML', 'HTML'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('GENERATED', 'Generated'),
        ('SIGNED', 'Signed'),
        ('DELIVERED', 'Delivered'),
    ]
    
    # Identifiers
    report_id = models.CharField(max_length=20, unique=True, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test)
    
    # Report Information
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    report_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='PDF')
    
    # Generation Information
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_date = models.DateTimeField(auto_now_add=True)
    
    # Approval Information
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_reports')
    signed_date = models.DateTimeField(null=True, blank=True)
    
    # File Information
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Additional Information
    notes = models.TextField(blank=True)
    is_confidential = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"{self.report_id} - {self.patient.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = f"RPT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class ReportSection(models.Model):
    """Configurable sections for reports"""
    SECTION_TYPES = [
        ('HEADER', 'Header'),
        ('PATIENT_INFO', 'Patient Information'),
        ('TEST_RESULTS', 'Test Results'), 
        ('INTERPRETATION', 'Clinical Interpretation'),
        ('FOOTER', 'Footer'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=100)
    content_template = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['template', 'section_type']
