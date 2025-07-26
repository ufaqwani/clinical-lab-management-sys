from django.db import models
from django.contrib.auth.models import User
from accounts.models import Lab
from patients.models import Patient

class TestCategory(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='test_categories', db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Test Categories"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['lab', 'name'], name='uniq_testcategory_name_per_lab'),
            models.UniqueConstraint(fields=['lab', 'code'], name='uniq_testcategory_code_per_lab'),
        ]

    def __str__(self):
        return self.name

class TestType(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='test_types', db_index=True)
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    sample_type = models.CharField(max_length=50)
    reference_range = models.CharField(max_length=200, blank=True)
    units = models.CharField(max_length=20, blank=True)
    normal_turnaround_time = models.IntegerField(help_text="Hours")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']
        constraints = [
            models.UniqueConstraint(fields=['lab', 'code'], name='uniq_testtype_code_per_lab'),
            models.UniqueConstraint(fields=['lab', 'name'], name='uniq_testtype_name_per_lab'),
        ]

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
    PRIORITY_CHOICES = [('ROUTINE', 'Routine'), ('URGENT', 'Urgent'), ('STAT', 'STAT')]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='tests', db_index=True)

    test_id = models.CharField(max_length=20, unique=True, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)

    ordered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordered_tests')
    ordered_date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='ROUTINE')

    sample_collected_date = models.DateTimeField(null=True, blank=True)
    sample_collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_samples')

    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_tests')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ORDERED')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-ordered_date']

    def __str__(self):
        return f"{self.test_id} - {self.patient.full_name} - {self.test_type.name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.patient_id and self.lab_id and self.patient.lab_id != self.lab_id:
            raise ValidationError("Test.lab must match Patient.lab")
        if self.test_type_id and self.lab_id and self.test_type.lab_id != self.lab_id:
            raise ValidationError("Test.lab must match TestType.lab")

class TestResult(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='test_results', db_index=True)
    test = models.OneToOneField(Test, on_delete=models.CASCADE, related_name='result')
    result_value = models.CharField(max_length=500)
    is_abnormal = models.BooleanField(default=False)
    technician_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.test.test_id}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.test_id and self.lab_id and self.test.lab_id != self.lab_id:
            raise ValidationError("TestResult.lab must match Test.lab")
