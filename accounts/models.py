from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Lab(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class LabMembership(models.Model):
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'
    TECH = 'TECH'
    RECEPTION = 'RECEPTION'
    ROLES = [
        (OWNER, 'Owner'),
        (ADMIN, 'Admin'),
        (TECH, 'Technician'),
        (RECEPTION, 'Reception'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default=TECH)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lab', 'user'], name='uniq_lab_user'),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.lab.name}"
