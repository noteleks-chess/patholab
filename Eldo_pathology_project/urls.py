from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import auth views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('patients.urls')),  # Your app's URLs
    # ... other URL patterns

    # Password reset URLs (Add these to the root urls.py)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]