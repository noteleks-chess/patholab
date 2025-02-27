from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor

class Patient(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients', verbose_name="Created By",default=1)
    mrn = models.CharField(max_length=255, unique=True, primary_key=True, verbose_name="Medical Record Number")
    first_name = models.CharField(max_length=255, verbose_name="First Name")
    last_name = models.CharField(max_length=255, verbose_name="Last Name")
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=20, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ], verbose_name="Gender")
    phone = models.CharField(max_length=255, blank=True, null=True, verbose_name="Phone Number")
    email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Email Address")
    address = models.TextField(blank=True, null=True, verbose_name="Address")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (MRN: {self.mrn})"

class CollectionSite(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Hospitals"

class Specimen(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='specimens', verbose_name="Created By",default=1)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    SPECIMEN_TYPES = [
        ('Blood', 'Blood'),
        ('Urine', 'Urine'),
        ('Tissue', 'Tissue'),
        ('Swab', 'Swab'),
        ('Fluids', 'Fluids'),
        ('FNA Sample', 'FNA Sample'),
        ('Other', 'Other'),
    ]
    specimen_type = models.CharField(max_length=255, choices=SPECIMEN_TYPES, verbose_name="Specimen Type")
    collection_date_time = models.DateTimeField(verbose_name="Collection Date and Time")
    received_date_time = models.DateTimeField(verbose_name="Received Date and Time")
    collection_site = models.ForeignKey(CollectionSite, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Collection Site")
    quantity = models.CharField(max_length=255, blank=True, null=True, verbose_name="Quantity")
    condition = models.CharField(max_length=255, blank=True, null=True, verbose_name="Condition")

    class Meta:
        db_table = 'patients_specimen'

    def __str__(self):
        return f"{self.specimen_type} (ID: {self.id}) - Patient: {self.patient.last_name}, {self.patient.first_name} (MRN: {self.patient.mrn})"

class TestOrder(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_orders', verbose_name="Created By",default=1)
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, related_name='test_orders', verbose_name="Specimen")
    TEST_NAMES = [
        ('histology', 'Histology'),
        ('cytology', 'Cytology'),
        ('pbf', 'Peripheral Blood Film'),
        ('immunohistochemistry', 'immunohistochemistry'),
    ]
    test_name = models.CharField(max_length=255, choices=TEST_NAMES, verbose_name="Test Type")
    ordering_doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    order_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Order Date and Time")

    def __str__(self):
        return f"{self.test_name} - Patient: {self.specimen.patient.last_name}, {self.specimen.patient.first_name} (MRN: {self.specimen.patient.mrn}) - Doctor: {self.ordering_doctor.last_name}, {self.ordering_doctor.first_name} (ID: {self.ordering_doctor.id})"

class TestResult(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results', verbose_name="Created By",default=1)
    test_order = models.OneToOneField(TestOrder, on_delete=models.CASCADE, related_name='test_result', verbose_name="Test Order")
    result_order_date_time = models.DateTimeField(blank=True, null=True, verbose_name="Order Date and Time")
    nature_of_specimen = models.TextField(verbose_name="Nature of Specimen")
    clinical_history = models.TextField(verbose_name="Clinical History")
    macroscopy_description = models.TextField(verbose_name="Macroscopic Description")
    microscopy_description = models.TextField(verbose_name="Microscopic Description")
    diagnosis = models.TextField(blank=True, null=True, verbose_name="Diagnosis and Conclusion")

    def __str__(self):
        return f"Test Result (ID: {self.id}) - Patient: {self.test_order.specimen.patient.last_name}, {self.test_order.specimen.patient.first_name} (MRN: {self.test_order.specimen.patient.mrn}) - Test: {self.test_order.test_name}"

class Report(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name="Created By",default=1)
    test_order = models.OneToOneField(TestOrder, on_delete=models.CASCADE, related_name='report', verbose_name="Test Order")
    comments_conclusion = models.TextField(verbose_name="Comments")
    doctor_signature_image = models.ImageField(upload_to='signatures/', blank=True, null=True, verbose_name="Doctor's Signature Image")
    report_generated_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Report Generated Date and Time")
    report_verified_date_time = models.DateTimeField(blank=True, null=True, verbose_name="Report Verified Date and Time")

    def __str__(self):
        return f"Report (ID: {self.id}) - Patient: {self.test_order.specimen.patient.last_name}, {self.test_order.specimen.patient.first_name} (MRN: {self.test_order.specimen.patient.mrn}) - Test: {self.test_order.test_name}"