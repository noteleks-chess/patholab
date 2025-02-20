from datetime import date, datetime
from io import BytesIO
import os
import logging
from dateutil.relativedelta import relativedelta 
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm, SpecimenEntryForm, TestOrderForm, HistologyResultForm, CytologyResultForm, PBFResultForm, ReportForm, LoginForm  # Combined imports
from .models import Patient, Specimen, TestOrder, Report, TestResult, CollectionSite # Import CollectionSite
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image  
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.colors import lightblue, blue, black, white, grey, red
from django.conf import settings
from django.urls import reverse
from PIL import Image as PILImage
from reportlab.lib.units import inch
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                user_groups = [group.name for group in request.user.groups.all()]

                if user.is_superuser or 'admin' in user_groups:
                    return redirect(reverse('admin:index'))
                elif 'doctor' in user_groups:
                    return redirect(reverse('patients:frontend_dashboard') + '?user_type=doctor')
                elif 'patient' in user_groups:
                    return redirect(reverse('patients:frontend_dashboard') + '?user_type=patient')
                elif 'receptionist' in user_groups:
                    return redirect(reverse('patients:frontend_dashboard') + '?user_type=receptionist')
                else:
                    return redirect(reverse('patients:frontend_dashboard'))  # Default redirect

            else:
                form.add_error(None, "Invalid username or password.")
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

@login_required
def frontend_dashboard(request):
    user_type = request.GET.get('user_type')
    context = {'user': request.user, 'is_superuser': request.user.is_superuser}
    user_groups = [group.name for group in request.user.groups.all()]

    if request.user.is_superuser or 'admin' in user_groups:
        context['is_admin'] = True
        template_name = 'patients/frontend_dashboard_admin.html'
        context['can_add_patient'] = request.user.has_perm('patients.add_patient')
        context['can_view_patient'] = request.user.has_perm('patients.view_patient')
        if context['can_view_patient']:
            context['patients'] = Patient.objects.all()

    elif 'doctor' in user_groups:
        context['is_doctor'] = True
        template_name = 'patients/frontend_dashboard_doctor.html'
        context['can_view_patient'] = request.user.has_perm('patients.view_patient')
        context['can_view_specimen'] = request.user.has_perm('patients.view_specimen')
        if context['can_view_patient']:
            context['patients'] = Patient.objects.all()
        if context['can_view_specimen']:
            context['specimens'] = Specimen.objects.all()

    elif 'patient' in user_groups:
        context['is_patient'] = True
        template_name = 'patients/frontend_dashboard_patient.html'
        context['can_view_report'] = request.user.has_perm('patients.view_report')
        try:
            patient = Patient.objects.get(user=request.user)
            if context['can_view_report']:
                context['reports'] = Report.objects.filter(test_order__specimen__patient=patient)
            else:
                context['reports'] = None
        except Patient.DoesNotExist:
            context['patient_error'] = "Patient profile not found."
            context['reports'] = None

    elif 'receptionist' in user_groups:
        context['is_receptionist'] = True
        template_name = 'patients/frontend_dashboard_receptionist.html'
        context['can_add_patient'] = request.user.has_perm('patients.add_patient')
        context['can_view_patient'] = request.user.has_perm('patients.view_patient')
        if context['can_view_patient']:
            context['patients'] = Patient.objects.all()

    else:  # Default template (if no specific user_type or group)
        template_name = 'patients/frontend_dashboard.html'

    return render(request, template_name, context)


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        user_groups = [group.name for group in user.groups.all()]  # Get user groups
        if user.is_superuser or 'admin' in user_groups:
            return reverse('patients:frontend_dashboard') + '?user_type=admin'
        elif 'doctor' in user_groups:
            return reverse('patients:frontend_dashboard') + '?user_type=doctor'
        elif 'patient' in user_groups:
            return reverse('patients:frontend_dashboard') + '?user_type=receptionist'
        else:
            return reverse('patients:frontend_dashboard')  # Default redirect (no user_type parameter)


@login_required
@permission_required('patients.add_patient')  # Protect this view
def create_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user  # Assign the current user
            patient.save()
            messages.success(request, "Patient profile created successfully!")
            return redirect(reverse('patients:frontend_dashboard') + '?user_type=patient')  # Redirect to frontend dashboard
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = PatientForm()
    return render(request, 'patients/create_patient.html', {'form': form})

@login_required
@permission_required('patients.add_patient')
def register_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient {patient.first_name} {patient.last_name} registered successfully!")
            return redirect(reverse('patients:patient_dashboard', kwargs={'patient_id': patient.id}))
        else:
            # Form is invalid, errors will be displayed automatically in the template
            for field, errors in form.errors.items(): # Loop through fields and errors
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}") # Display each error message
    else:
        form = PatientForm()
    return render(request, 'patients/register_patient.html', {'form': form})

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, 'patients/patient_detail.html', {'patient': patient})

@login_required
@permission_required('patients.change_patient')
def patient_update(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient {patient.first_name} updated successfully!")
            return redirect('patients:patient_list')  # Redirect to patient list
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'patient': patient})  # Reuse or create a patient_form.html template

@login_required
@permission_required('patients.delete_patient')
def patient_delete(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, f"Patient {patient.first_name} deleted successfully!")
        return redirect('patients:patient_list')
    return redirect('patients:patient_list')  # Redirect even if not POST (e.g., GET request)

@login_required
@permission_required('patients.add_specimen')
def enter_specimen(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = SpecimenEntryForm(request.POST or None) # Important: Handle both GET and POST
        if form.is_valid():
            specimen = form.save(commit=False)
            specimen.patient = patient
            specimen.save()
            return redirect(reverse('patients:specimen_detail', kwargs={'specimen_id': specimen.id}))
    else:
        form = SpecimenEntryForm(initial={'patient': patient})
    return render(request, 'patients/enter_specimen.html', {'form': form, 'patient': patient})

@login_required
def specimen_detail(request, specimen_id):
    specimen = get_object_or_404(Specimen, pk=specimen_id)
    return render(request, 'patients/specimen_detail.html', {'specimen': specimen})

@login_required
@permission_required('patients.view_patient')
def patient_list(request):
    patients = Patient.objects.all()  # Or any other logic to get your patient list
    return render(request, 'patients/patient_list.html', {'patients': patients})

@login_required
@permission_required('patients.add_testorder')
def create_test_order(request, specimen_id):
    specimen = get_object_or_404(Specimen, pk=specimen_id)  # Make sure the Specimen exists!
    if request.method == 'POST':
        form = TestOrderForm(request.POST)
        if form.is_valid():
            test_order = form.save(commit=False)
            test_order.specimen = specimen
            test_order.save()
            return redirect(reverse('patients:test_order_detail', kwargs={'test_order_id': test_order.id}))
    else:
        form = TestOrderForm(initial={'specimen': specimen})  # Prefill specimen (important)
    return render(request, 'patients/create_test_order.html', {'form': form, 'specimen': specimen})  # 'form' in context!


@login_required
def test_order_detail(request, test_order_id):  # Corrected: Removed duplicate
    test_order = get_object_or_404(TestOrder, pk=test_order_id)
    return render(request, 'patients/test_order_detail.html', {'test_order': test_order})

@login_required
@permission_required('patients.add_testresult')
def enter_results(request, test_order_id, test_type):
    test_order = get_object_or_404(TestOrder, pk=test_order_id)

    if test_type == 'histology':
        form_class = HistologyResultForm
        template = 'patients/enter_histology_results.html'
    elif test_type == 'cytology':
        form_class = CytologyResultForm
        template = 'patients/enter_cytology_results.html'
    elif test_type == 'pbf':
        form_class = PBFResultForm
        template = 'patients/enter_pbf_results.html'
    else:
        # Handle invalid test type (e.g., redirect with error message)
        return redirect(reverse('patients:test_order_detail', kwargs={'test_order_id': test_order_id}))  # Or raise an exception

    test_result, created = TestResult.objects.get_or_create(test_order=test_order)
    form = form_class(request.POST or None, instance=test_result)

    if form.is_valid():
        test_result = form.save(commit=False)
        test_result.test_order = test_order
        test_result.save()
        return redirect(reverse('patients:report_form', kwargs={'test_order_id': test_order.id}))  # Or wherever you want to redirect

    return render(request, template, {'form': form, 'test_order': test_order})


@login_required
@permission_required('patients.change_report')
def report_form(request, test_order_id):
    test_order = get_object_or_404(TestOrder, pk=test_order_id)
    report, created = Report.objects.get_or_create(test_order=test_order)
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            return redirect(reverse('patients:report_draft', kwargs={'report_id': report.id}))  # Redirect to report_draft
    else:
        form = ReportForm(instance=report)
    return render(request, 'patients/report_form.html', {'form': form, 'test_order': test_order, 'report': report})  # Add 'report': report to the context!


@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if request.user.has_perm('patients.view_report') and report.test_order.specimen.patient == request.user: #Check permissions and if the patient is the same as the user
        # User has permission and it's their report
        return render(request, 'patients/report_detail.html', {'report': report})
    else:
        # User doesn't have permission or it's not their report
        return HttpResponseForbidden("You do not have permission to view this report.") #Return a 403 Forbidden error


@login_required
def patient_dashboard(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    specimens = Specimen.objects.filter(patient=patient)
    test_orders = TestOrder.objects.filter(specimen__patient=patient)
    reports = Report.objects.filter(test_order__specimen__patient=patient)
    context = {
        'patient': patient,  # Include the patient object in the context
        'specimens': specimens,
        'test_orders': test_orders,
        'reports': reports,
    }
    return render(request, 'patients/patient_dashboard.html', context)

@login_required
def report_draft(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    test_order = report.test_order
    specimen = test_order.specimen
    patient = specimen.patient
    try:
        test_result = test_order.test_result  # Get the TestResult
    except TestResult.DoesNotExist:
        test_result = None  # Handle the case where there is no test result yet.

    context = {
        'report': report,
        'test_order': test_order,
        'specimen': specimen,
        'patient': patient,
        'test_result': test_result, # Include the TestResult
    }
    return render(request, 'patients/report_draft.html', context)

@login_required
@permission_required('patients.change_report')
def finalize_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if request.method == 'POST':
        signature = request.POST.get('signature')
        report.doctor_signature = signature
        report.save()

        try:  # Add try...except block
            buffer = BytesIO()
            response = generate_report(report, buffer)
            return response
        except Exception as e: # Catch any exceptions
            print(f"Error in finalize_report: {e}")
            import traceback
            traceback.print_exc()
            # Handle error appropriately, e.g.,
            messages.error(request, f"An error occurred during report generation: {e}") # Display error message
            return redirect(reverse('patients:report_draft', kwargs={'report_id': report_id})) # Redirect back to the report draft page
    else:
        return redirect(reverse('patients:report_draft', kwargs={'report_id': report_id}))
    
#@login_required
#@permission_required('patients.view_report')
def generate_report(report, buffer):
    try:
        test_order = report.test_order
        specimen = test_order.specimen
        patient = specimen.patient
        test_result = getattr(test_order, 'test_result', None)

        p = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []



        # Header (use a variable or setting for the title)
        report_title = getattr(settings, 'REPORT_TITLE', "Laboratory Final Report")  # Get from settings or default
        header = Paragraph(report_title, styles['h1'])
        header.style.textColor = lightblue
        header.style.alignment = 1
        elements.append(header)
        elements.append(Spacer(1, 24))

        def create_row(label, value):
            return [Paragraph(f"<b>{label}</b>", styles['Normal']), Paragraph(str(value) if value else "N/A", styles['Normal'])]

        # Patient & Specimen Details Table
       




        patient_data = [
            create_row("MRN:", patient.mrn),
            create_row("Name:", f"{patient.first_name} {patient.last_name}"),
            create_row("DOB:", patient.dob),
            create_row("Gender:", patient.gender),
            
        ]
        specimen_data = [
            create_row("Specimen Type:", specimen.specimen_type),
            create_row("Collection Date:", specimen.collection_date_time),
        ]
        data = []
        max_rows = max(len(patient_data), len(specimen_data))
        for i in range(max_rows):
            row = []
            if i < len(patient_data):
                row.extend(patient_data[i])
            else:
                row.extend(["", ""])

            if i < len(specimen_data):
                row.extend(specimen_data[i])
            else:
                row.extend(["", ""])
            data.append(row)

        table = Table(data, colWidths=[100, 200, 100, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), lightblue),
            ('BACKGROUND', (2, 0), (2, -1), lightblue),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, grey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Test Order Details Table
        test_order_data = [
            create_row("Test Name:", test_order.test_name),
            create_row("Order Date:", test_order.order_date_time),
            create_row("Ordering Doctor:", test_order.ordering_doctor),
        ]
        table = Table(test_order_data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), lightblue),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, grey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Test Result Details Table
        if test_result:
            test_result_data = [
                create_row("Nature of Specimen:", test_result.nature_of_specimen),
                create_row("Clinical History:", test_result.clinical_history),
                create_row("Macroscopy Description:", test_result.macroscopy_description),
                create_row("Microscopy Description:", test_result.microscopy_description),
                create_row("Diagnosis:", test_result.diagnosis),
            ]


            table = Table(test_result_data, colWidths=[150, 350])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), lightblue),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, grey)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph("Test results are not available yet.", styles['Normal']))
            elements.append(Spacer(1, 12))

        # Report Details Table
        report_data = [
            create_row("Comments/Conclusion:", report.comments_conclusion),
            create_row("Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        if report.doctor_signature:
            report_data.append(create_row("Doctor's Signature:", report.doctor_signature))

        table = Table(report_data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), lightblue),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, grey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))


        

        p.build(elements)
        buffer.seek(0)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report_{report.id}.pdf"'
        response.write(buffer.getvalue())
        return response
    
    except Exception as e:
        print(f"Error in generate_report: {e}")
        import traceback
        traceback.print_exc()

        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"An error occurred during report generation: {e}")
        p.showPage()
        p.save()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report_{report.id}.pdf"'
        response.write(buffer.getvalue())
        return response