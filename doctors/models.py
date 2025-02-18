from django.db import models

class Doctor(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="First Name")
    last_name = models.CharField(max_length=255, verbose_name="Last Name")
    specialization = models.CharField(max_length=255, blank=True, null=True, verbose_name="Specialization")  # Optional

    def __str__(self):
        return f"{self.first_name} {self.last_name}"