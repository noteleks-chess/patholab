from django.contrib import admin
from django.http import HttpResponse
from .models import Patient, Specimen, TestOrder, TestResult, Report, CollectionSite
from doctors.models import Doctor
from .views import generate_report
from django.db.models import JSONField
from django import forms
from .forms import (
    PatientForm,
    SpecimenEntryForm,
    TestOrderForm,
    HistologyResultForm,
    CytologyResultForm,
    PBFResultForm,
    ReportForm,
)
import zipfile
from io import BytesIO

admin.site.register(CollectionSite)

@admin.action(description="Download Selected Reports as PDF (ZIP)")
def download_reports(modeladmin, request, queryset):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zipf:
        for report in queryset:
            report_pk = report.pk

            if report.test_order and report.test_order.specimen and (report.test_order.specimen.patient == request.user or request.user.is_staff):
                pdf_buffer = BytesIO()
                generate_report(report, pdf_buffer)

                if pdf_buffer.getvalue():
                    zipf.writestr(f"report_{report_pk}.pdf", pdf_buffer.getvalue())
                else:
                    print(f"Error generating PDF for report {report_pk}")
                    continue
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
    list_display = ('test_name', 'ordering_doctor', 'order_date_time')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    inlines = [SpecimenInline]
    list_display = ('mrn', 'first_name', 'last_name', 'dob', 'gender', 'created_by')
    search_fields = ('mrn', 'first_name', 'last_name')
    list_filter = ('gender', 'dob', 'created_by')
    ordering = ('last_name', 'first_name')
    form = PatientForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs.filter(specimen__created_by=request.user).distinct() # Filter by specimen, make distinct
        return qs

@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    form = SpecimenEntryForm
    list_display = ('patient', 'specimen_type', 'collection_date_time', 'received_date_time', 'collection_site', 'created_by')
    search_fields = ('specimen_type', 'patient__first_name', 'patient__last_name', 'patient__mrn', 'collection_site__name')
    list_filter = ('specimen_type', 'collection_date_time', 'collection_site', 'created_by')
    raw_id_fields = ('patient',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs.filter(created_by=request.user)
        return qs

@admin.register(TestOrder)
class TestOrderAdmin(admin.ModelAdmin):
    form = TestOrderForm
    list_display = ('specimen', 'test_name', 'ordering_doctor', 'order_date_time', 'created_by')
    search_fields = ('specimen__patient__first_name', 'specimen__patient__last_name', 'test_name')
    list_filter = ('test_name', 'order_date_time', 'created_by')
    raw_id_fields = ('specimen',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs.filter(specimen__created_by=request.user)
        return qs

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test_order', 'result_order_date_time', 'diagnosis', 'created_by')
    search_fields = (
        'test_order__specimen__patient__first_name',
        'test_order__specimen__patient__last_name',
        'test_order__test_name',
        'diagnosis',
    )
    list_filter = ('created_by',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs.filter(test_order__specimen__created_by=request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.test_order:
            if obj.test_order.test_name == 'histology':
                return HistologyResultForm
            elif obj.test_order.test_name == 'cytology':
                return CytologyResultForm
            elif obj.test_order.test_name == 'pbf':
                return PBFResultForm
        return super().get_form(request, obj, **kwargs)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    form = ReportForm
    list_display = ('test_order', 'report_generated_date_time', 'report_verified_date_time', 'created_by')
    search_fields = ('test_order__specimen__patient__first_name', 'test_order__specimen__patient__last_name', 'test_order__test_name', 'test_order__specimen__collection_site')
    list_filter = ('report_verified_date_time', 'created_by')
    actions = [download_reports]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs.filter(test_order__specimen__created_by=request.user)
        return qs

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    pass