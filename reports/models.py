from django.db import models
from django.contrib.auth.models import User
from accounts.models import Lab
from patients.models import Patient
from tests.models import Test
import uuid

def lab_upload_path(instance, filename):
    lab_id = getattr(instance, 'lab_id', None) or 'unassigned'
    return f"labs/{lab_id}/reports/{filename}"

class ReportTemplate(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='report_templates', db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, default='standard')
    header_logo = models.ImageField(upload_to=lab_upload_path, blank=True, null=True)
    footer_text = models.TextField(blank=True, default="This report is electronically generated and signed.")
    is_default = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lab', 'name'], name='uniq_reporttemplate_name_per_lab'),
        ]

    def __str__(self):
        return self.name

class Report(models.Model):
    FORMAT_CHOICES = [('PDF', 'PDF'), ('HTML', 'HTML')]
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('GENERATED', 'Generated'), ('SIGNED', 'Signed'), ('DELIVERED', 'Delivered')]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='reports', db_index=True)

    report_id = models.CharField(max_length=20, unique=True, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test)

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    report_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='PDF')

    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_date = models.DateTimeField(auto_now_add=True)

    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_reports')
    signed_date = models.DateTimeField(null=True, blank=True)

    report_file = models.FileField(upload_to=lab_upload_path, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

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

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.patient_id and self.lab_id and self.patient.lab_id != self.lab_id:
            raise ValidationError("Report.lab must match Patient.lab")
        if self.template_id and self.lab_id and self.template.lab_id != self.lab_id:
            raise ValidationError("Report.lab must match Template.lab")
        if self.pk and self.lab_id:
            if self.tests.exclude(lab_id=self.lab_id).exists():
                raise ValidationError("All linked tests must belong to the same lab as the report")

class ReportSection(models.Model):
    SECTION_TYPES = [
        ('HEADER', 'Header'),
        ('PATIENT_INFO', 'Patient Information'),
        ('TEST_RESULTS', 'Test Results'),
        ('INTERPRETATION', 'Clinical Interpretation'),
        ('FOOTER', 'Footer'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='report_sections', db_index=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=100)
    content_template = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['lab', 'template', 'section_type'], name='uniq_section_type_per_template_per_lab'),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template_id and self.lab_id and self.template.lab_id != self.lab_id:
            raise ValidationError("ReportSection.lab must match Template.lab")
