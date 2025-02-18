from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth import urls 
from django.urls import path, include
from django.contrib import admin

app_name = 'patients'

urlpatterns = [
    path('', views.index, name='index'), 
     # Note the change
    #path('login/', auth_views.LoginView.as_view(template_name='patients/login.html'), name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_patient, name='register_patient'),  # Register URL FIRST
    path('admin/', admin.site.urls),
    path('dashboard/', views.frontend_dashboard, name='frontend_dashboard'),
    path('patient/<int:patient_id>/dashboard/', views.patient_dashboard, name='patient_dashboard'), #Dashboard
    path('patient/<int:patient_id>/update/', views.patient_update, name='patient_update'),  # URL for editing a patient
    path('patient/<int:patient_id>/delete/', views.patient_delete, name='patient_delete'),  # URL for deleting a patient
    path('<int:patient_id>/', views.patient_detail, name='patient_detail'),  # Then patient detail
    path('<int:patient_id>/specimen/', views.enter_specimen, name='enter_specimen'),
    path('specimen/<int:specimen_id>/', views.specimen_detail, name='specimen_detail'),
    path('specimen/<int:specimen_id>/test_order/add/', views.create_test_order, name='create_test_order'),
    path('test_order/<int:test_order_id>/', views.test_order_detail, name='test_order_detail'),
    path('report_form/<int:test_order_id>/', views.report_form, name='report_form'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('report/<int:report_id>/draft/', views.report_draft, name='report_draft'),
    path('report/<int:report_id>/finalize/', views.finalize_report, name='finalize_report'),
    path('report/generate/<int:report_id>/', views.generate_report, name='generate_report'),
    path('test_order/<int:test_order_id>/<str:test_type>/', views.enter_results, name='enter_results'),
    path('patients/', views.patient_list, name='patient_list'), 
    path('create/', views.create_patient, name='create_patient'),
    #path('login/', include(urls)),  # Include Django's built-in login URLs
    #path('login/', views.CustomLoginView.as_view(), name='login'),# Your custom login view
]