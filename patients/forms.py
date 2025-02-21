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
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        label="Select Patient",
        empty_label="Select a Patient",
    )

    class Meta:
        model = Specimen
        fields = ['patient', 'specimen_type', 'collection_date_time', 'received_date_time', 'collection_site', 'quantity', 'condition']
    collection_date_time = forms.DateTimeField(
        input_formats=['%m/%d/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    received_date_time = forms.DateTimeField(
        input_formats=['%m/%d/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )

    def label_from_instance(self, obj):
        return f"{obj.patient.mrn} - {obj.patient.first_name} {obj.patient.last_name}"
    
class TestOrderForm(forms.ModelForm):
    ordering_doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="Ordering Doctor")
    specimen = forms.ModelChoiceField(
        queryset=Specimen.objects.all(),
        label="Select Specimen",
        empty_label="Select a Specimen",
    )

    class Meta:
        model = TestOrder
        fields = ['specimen', 'test_name', 'ordering_doctor']


    def label_from_instance(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name} (MRN: {obj.patient.mrn}) - {obj.specimen_type} (ID: {obj.pk}) - {obj.collection_date_time}"


class HistologyResultForm(forms.ModelForm):
    test_order = forms.ModelChoiceField(
        queryset=TestOrder.objects.all(),
        label="Select Test Order",
        empty_label="Select a Test Order",
    )

    class Meta:
        model = TestResult
        fields = ['test_order', 'nature_of_specimen', 'clinical_history', 'macroscopy_description', 'microscopy_description']
        widgets = {
            'nature_of_specimen': forms.Textarea(attrs={'rows': 4}),
            'clinical_history': forms.Textarea(attrs={'rows': 4}),
            'macroscopy_description': forms.Textarea(attrs={'rows': 4}),
            'microscopy_description': forms.Textarea(attrs={'rows': 4}),
        }

    def label_from_instance(self, obj):
        return f"{obj.test_order.specimen.patient.mrn} - {obj.test_order.specimen.patient.first_name} {obj.test_order.specimen.patient.last_name} - {obj.test_order.test_name} - {obj.test_order.order_date_time}"


class CytologyResultForm(forms.ModelForm):
    test_order = forms.ModelChoiceField(
        queryset=TestOrder.objects.all(),
        label="Select Test Order",
        empty_label="Select a Test Order",
    )

    class Meta:
        model = TestResult
        fields = ['test_order', 'nature_of_specimen', 'clinical_history', 'macroscopy_description', 'microscopy_description']
        widgets = {
            'nature_of_specimen': forms.Textarea(attrs={'rows': 4}),
            'clinical_history': forms.Textarea(attrs={'rows': 4}),
            'macroscopy_description': forms.Textarea(attrs={'rows': 4}),
            'microscopy_description': forms.Textarea(attrs={'rows': 4}),
        }

    def label_from_instance(self, obj):
        return f"{obj.test_order.specimen.patient.mrn} - {obj.test_order.specimen.patient.first_name} {obj.test_order.specimen.patient.last_name} - {obj.test_order.test_name} - {obj.test_order.order_date_time}"


class PBFResultForm(forms.ModelForm):
    test_order = forms.ModelChoiceField(
        queryset=TestOrder.objects.all(),
        label="Select Test Order",
        empty_label="Select a Test Order",
    )

    class Meta:
        model = TestResult
        fields = ['test_order', 'nature_of_specimen', 'clinical_history', 'macroscopy_description', 'microscopy_description']
        widgets = {
            'nature_of_specimen': forms.Textarea(attrs={'rows': 4}),
            'clinical_history': forms.Textarea(attrs={'rows': 4}),
            'macroscopy_description': forms.Textarea(attrs={'rows': 4}),
            'microscopy_description': forms.Textarea(attrs={'rows': 4}),
        }

    def label_from_instance(self, obj):
        return f"{obj.specimen.patient.mrn} - {obj.specimen.patient.first_name} {obj.specimen.patient.last_name} - {obj.test_name} - {obj.order_date_time}"


class ReportForm(forms.ModelForm):
    test_order = forms.ModelChoiceField(
        queryset=TestOrder.objects.all(),
        label="Select Test Order",
        empty_label="Select a Test Order",
    )

    class Meta:
        model = Report
        fields = ['test_order', 'comments_conclusion']
        widgets = {
            'comments_conclusion': forms.Textarea(attrs={'rows': 5}),
        }

    def label_from_instance(self, obj):
        return f"{obj.test_order.specimen.patient.mrn} - {obj.test_order.specimen.patient.first_name} {obj.test_order.specimen.patient.last_name} - {obj.test_order.test_name} - {obj.test_order.order_date_time}"

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'mrn', 'dob', 'gender', 'phone']  # List all the fields you want in the form