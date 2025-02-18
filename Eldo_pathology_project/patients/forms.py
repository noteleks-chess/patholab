from django import forms
from .models import Patient
from .models import Specimen
from .models import TestOrder
from doctors.models import Doctor
from .models import TestResult
from .models import Report

from django import forms
from .models import Patient, Specimen, TestOrder, TestResult, Report
from doctors.models import Doctor  # Import Doctor model

class LoginForm(forms.Form):
    username = forms.CharField(max_length=254, required=True, label='Username/Email')  # Or forms.EmailField
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Password')


class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'  # Or specify fields explicitly if you don't want all of them:
        # fields = ['mrn', 'first_name', 'last_name', 'dob', 'gender', 'phone', 'email', 'address']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),  # Makes the DOB a date picker
        }


class SpecimenEntryForm(forms.ModelForm):
    class Meta:
        model = Specimen
        fields = ['patient', 'specimen_type', 'collection_date_time', 'received_date_time', 'collection_site', 'quantity', 'condition']
        widgets = {
            'collection_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'received_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class TestOrderForm(forms.ModelForm):
    ordering_doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="Ordering Doctor")

    class Meta:
        model = TestOrder
        fields = ['specimen', 'test_name', 'ordering_doctor']


class HistologyResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['nature_of_specimen', 'clinical_history', 'macroscopy_description', 'microscopy_description', 'histology_parameter1', 'histology_parameter2', 'histology_parameter3']
        widgets = {
            'nature_of_specimen': forms.Textarea(attrs={'rows': 4}),
            'clinical_history': forms.Textarea(attrs={'rows': 4}),
            'macroscopy_description': forms.Textarea(attrs={'rows': 4}),
            'microscopy_description': forms.Textarea(attrs={'rows': 4}),
        }


class CytologyResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['nature_of_specimen', 'clinical_history', 'macroscopy_description', 'microscopy_description', 'cytology_parameter1', 'cytology_parameter2',  # Add your cytology-specific fields
                  'cytology_parameter3']  # Example: 'cell_type', 'nuclear_morphology', etc.
        widgets = {
            'nature_of_specimen': forms.Textarea(attrs={'rows': 4}),
            'clinical_history': forms.Textarea(attrs={'rows': 4}),
            'macroscopy_description': forms.Textarea(attrs={'rows': 4}),
            'microscopy_description': forms.Textarea(attrs={'rows': 4}),
        }


class PBFResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['nature_of_specimen', 'clinical_history', 'macroscopy_description', 'microscopy_description', 'pbf_parameter1', 'pbf_parameter2',  # Add your PBF-specific fields
                  'pbf_parameter3']  # Example: 'wbc_count', 'rbc_count', etc.
        widgets = {
            'nature_of_specimen': forms.Textarea(attrs={'rows': 4}),
            'clinical_history': forms.Textarea(attrs={'rows': 4}),
            'macroscopy_description': forms.Textarea(attrs={'rows': 4}),
            'microscopy_description': forms.Textarea(attrs={'rows': 4}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['comments_conclusion']  # Include only the fields you want to edit
        widgets = {
            'comments_conclusion': forms.Textarea(attrs={'rows': 5}),  # Make it a textarea
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'mrn', 'dob', 'gender', 'phone']  # List all the fields you want in the form