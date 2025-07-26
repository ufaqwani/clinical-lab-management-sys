from django.db import models
from django.core.validators import RegexValidator
from accounts.models import Lab

class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='patients', db_index=True)

    # Keep as PK to avoid SQLite FK mismatch
    patient_id = models.CharField(max_length=20, primary_key=True)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()

    blood_group = models.CharField(max_length=5, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_date']
        # No need for (lab, patient_id) unique because patient_id is PK

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
