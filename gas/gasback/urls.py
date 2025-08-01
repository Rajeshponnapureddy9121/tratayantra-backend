from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),

    # Dashboard
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),

    # Gas Leak Detection
    path('gas-leak/status/', views.gas_leak_status, name='gas_leak_status'),
    path('gas-leak/scan/', views.trigger_gas_scan, name='trigger_gas_scan'),

    # Gas Level Monitoring
    path('gas-level/data/', views.gas_level_data, name='gas_level_data'),

    # Pipeline Health Monitoring
    path('pipeline/health/', views.pipeline_health_data, name='pipeline_health_data'),

    # Regulator Status (to be implemented if needed)
    path('regulator/status/', views.regulator_status, name='regulator_status'),

    # Regulator Control
    path('regulator/control/', views.regulator_control, name='regulator_control'),

    # Emergency Contacts
    path('emergency/contacts/', views.emergency_contacts, name='emergency_contacts'),
    path('emergency/contacts/add/', views.add_emergency_contact, name='add_emergency_contact'),
    path('emergency/contacts/', views.emergency_contacts_management, name='emergency_contacts'),
    path('emergency/contacts/<int:contact_id>/', views.update_emergency_contact, name='update_emergency_contact'),
    path('emergency/contacts/<int:contact_id>/delete/', views.delete_emergency_contact, name='delete_emergency_contact'),

    # Emergency SOS (add if your app needs this)
    path('emergency/sos/', views.trigger_emergency_sos, name='emergency_sos'),

    # Profile Management
    path('profile/', views.user_profile_management, name='profile_management'),
    path('profile/upload-image/', views.upload_profile_image, name='upload_profile_image'),

    # Sensor Data endpoint (add based on your app usage)
    path('sensors/data/', views.sensor_data, name='sensor_data'),
    path("sensor-data/", views.sensor_data_view),
    path("regulator/status/", views.regulator_status_view),
]
