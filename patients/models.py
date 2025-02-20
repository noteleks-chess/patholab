from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor

class Patient(models.Model):  # Model name: Capitalized (PascalCase)
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
    name = models.CharField(max_length=255, unique=True)  # Prevent duplicate names

    def __str__(self):
        return self.name  # Display the name in the dropdown

class Specimen(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='specimens', verbose_name="Patient", to_field='mrn')
    SPECIMEN_TYPES = [  # Choices for specimen type
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

    COLLECTION_SITES = [  # Choices for collection site
        ('Reale Hospital', 'Reale Hospital'),
        ('Eldoret Hospital', 'Eldoret Hospital'),
        ('St Luke\'s Hospital', 'St Luke\'s Hospital'),
        ('Top Hill Hospital', 'Top Hill Hospital'),
        ('Lodwar Hospitals', 'Lodwar Hospitals'),
        ('Radiocare', 'Radiocare'),
        ('St Brigitta Yamumbi', 'St Brigitta Yamumbi'),
        ('Grand Royal Hospital', 'Grand Royal Hospital'),
        ('Living Room Hospital', 'Living Room Hospital'),
        ('Racecourse Hospital', 'Racecourse Hospital'),
        ('Elgon View Hospital', 'Elgon View Hospital'),
        ('Palmcare Hospital', 'Palmcare Hospital'),
        ('Other', 'Other'),
    ]
    collection_site = models.ForeignKey(CollectionSite, on_delete=models.PROTECT, 
                                        blank=True, null=True, verbose_name="Collection Site")
    quantity = models.CharField(max_length=255, blank=True, null=True, verbose_name="Quantity")
    condition = models.CharField(max_length=255, blank=True, null=True, verbose_name="Condition")

    class Meta:
        db_table = 'patients_specimen'

    def __str__(self):
        if self.pk:  # Check if the Specimen has a primary key (is saved)
            try:
                patient = Patient.objects.get(mrn=self.patient)
                return f"Specimen {self.specimen_type} (ID: {self.pk}) for {patient}"
            except Patient.DoesNotExist:
                return f"Specimen {self.specimen_type} (ID: {self.pk}) for Unknown Patient"
        else:  # If the Specimen is being created
            return f"Specimen {self.specimen_type} (Unsaved) for MRN: {self.patient}"

    


    
class TestOrder(models.Model):
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, related_name='test_orders', verbose_name="Specimen")
    TEST_NAMES = [  # Choices for test type
        ('histology', 'Histology'),
        ('cytology', 'Cytology'),
        ('pbf', 'Peripheral Blood Film'),
        ('immunohistochemistry', 'immunohistochemistry'),
    ]
    test_name = models.CharField(max_length=255, choices=TEST_NAMES, verbose_name="Test Type")
    ordering_doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)  # Foreign key to Doctor)
    order_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Order Date and Time")

class TestResult(models.Model):  # TestResult model (Defined SECOND)
    test_order = models.OneToOneField(TestOrder, on_delete=models.CASCADE, related_name='test_result', verbose_name="Test Order")
    result_order_date_time = models.DateTimeField(blank=True, null=True, verbose_name="Order Date and Time") # New field
    nature_of_specimen = models.TextField(verbose_name="Nature of Specimen")
    clinical_history = models.TextField(verbose_name="Clinical History")
    macroscopy_description = models.TextField(verbose_name="Macroscopic Description")
    microscopy_description = models.TextField(verbose_name="Microscopic Description")
    diagnosis = models.TextField(blank=True, null=True)  





class Report(models.Model):  # Report model (Defined LAST)
    test_order = models.OneToOneField(TestOrder, on_delete=models.CASCADE, related_name='report', verbose_name="Test Order")
    comments_conclusion = models.TextField(verbose_name="Comments and Conclusion")
    doctor_signature = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doctor's Signature")
    report_generated_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Report Generated Date and Time")
    report_verified_date_time = models.DateTimeField(blank=True, null=True, verbose_name="Report Verified Date and Time")

    def __str__(self):
        return self.test_order.test_name