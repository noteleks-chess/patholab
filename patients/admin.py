from django.contrib import admin
from django.http import HttpResponse
from .models import Patient, Specimen, TestOrder, TestResult, Report, CollectionSite
from doctors.models import Doctor  # Import Doctor model
from .views import generate_report  # Import your PDF generation function from views.py
from django.db.models import JSONField  # Import JSONField
from django import forms  # Import forms
import zipfile
from io import BytesIO

admin.site.register(CollectionSite)

@admin.action(description="Download Selected Reports as PDF (ZIP)")
def download_reports(modeladmin, request, queryset):
    buffer = BytesIO() # create main buffer for zip file
    with zipfile.ZipFile(buffer, 'w') as zipf:
        for report in queryset:
            report_pk = report.pk

            if report.test_order and report.test_order.specimen and (report.test_order.specimen.patient == request.user or request.user.is_staff):
                pdf_buffer = BytesIO()  # Create a *new* buffer for *each* report
                generate_report(report, pdf_buffer)  # Pass both report and pdf_buffer

                if pdf_buffer.getvalue(): # check if buffer has value
                    zipf.writestr(f"report_{report_pk}.pdf", pdf_buffer.getvalue())
                else:
                    print(f"Error generating PDF for report {report_pk}")
                    continue  # Skip to the next report
            else:
                print(f"User {request.user} does not have permission to download report {report}")
                continue

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="reports.zip"'

    if zipf.namelist():
        response.write(buffer.getvalue())
        return response
    else:
        return HttpResponse("No reports could be generated or downloaded due to permission issues or errors.", status=204)

    
class SpecimenInline(admin.TabularInline):
    model = Specimen
    extra = 0
    list_display = ('specimen_type', 'collection_date_time', 'received_date_time')
    readonly_fields = ('collection_date_time', 'received_date_time')

class TestOrderInline(admin.TabularInline):
    model = TestOrder
    extra = 0
    list_display = ('test_name', 'ordering_doctor', 'order_date_time')  # Correct for inlines
    

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    inlines = [SpecimenInline]
    list_display = ('mrn', 'first_name', 'last_name', 'dob', 'gender')
    search_fields = ('mrn', 'first_name', 'last_name')
    list_filter = ('gender', 'dob')
    ordering = ('last_name', 'first_name')

from django import forms
from .models import Specimen  # Import your Specimen model

class SpecimenAdminForm(forms.ModelForm):

    class Meta:
        model = Specimen
        fields = '__all__'  # Include all fields from the model
        # Or specify the fields explicitly if you prefer:
        # fields = ['patient', 'specimen_type', 'collection_date_time', ...]

    def clean(self):
        cleaned_data = super().clean()
        collection_site = cleaned_data.get('collection_site')
        other_collection_site = cleaned_data.get('other_collection_site')

        if collection_site == 'Other' and not other_collection_site:
            raise forms.ValidationError("Please specify the other collection site.")
        return cleaned_data

def save(self, commit=True):
    instance = super().save(commit=False)
    collection_site = self.cleaned_data.get('collection_site')
    other_collection_site = self.cleaned_data.get('other_collection_site')

    if str(collection_site) == 'Other': # Corrected this line
        instance.collection_site = None  # Set the ForeignKey to None
        instance.other_collection_site = other_collection_site # Store the value in the new field
    else:
        instance.collection_site = collection_site # Assign the selected CollectionSite
        instance.other_collection_site = None  # Clear the other_collection_site

    if commit:
        instance.save()
    return instance
    
@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    form = SpecimenAdminForm  # Use your custom form
    list_display = ('patient', 'specimen_type', 'collection_date_time', 'received_date_time', 'collection_site')
    search_fields = ('patient__first_name', 'patient__last_name', 'specimen_type', 'collection_site')
    list_filter = ('specimen_type', 'collection_date_time', 'collection_site')
    raw_id_fields = ('patient',)

@admin.register(TestOrder)
class TestOrderAdmin(admin.ModelAdmin):
    list_display = ('specimen', 'test_name', 'ordering_doctor', 'order_date_time')  # Correct
    search_fields = ('specimen__patient__first_name', 'specimen__patient__last_name', 'test_name')
    list_filter = ('test_name', 'order_date_time')
    

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test_order', 'result_order_date_time', 'diagnosis')  # Include diagnosis in list display
    search_fields = (
        'test_order__specimen__patient__first_name',
        'test_order__specimen__patient__last_name',
        'test_order__test_name',
        'diagnosis', )
    # If using JSONField for parameters:
    # formfield_overrides = {
    #     JSONField: {'widget': forms.Textarea},  # Use a textarea for JSONField
    # }

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('test_order', 'report_generated_date_time', 'report_verified_date_time')
    search_fields = ('test_order__specimen__patient__first_name', 'test_order__specimen__patient__last_name', 'test_order__test_name','test_order__specimen__collection_site')
    list_filter = ('report_verified_date_time',)
    actions = [download_reports]

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    pass