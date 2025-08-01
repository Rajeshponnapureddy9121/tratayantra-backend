# gasback/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    device_unique_code = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False, default='9999999999')
    profile_image = models.URLField(blank=True, null=True)
    notification_preferences = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

# Gas Monitoring Models
class GasSensor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor_id = models.CharField(max_length=100, unique=True)
    sensor_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    sensor_type = models.CharField(max_length=50, choices=[
        ('GAS_LEAK', 'Gas Leak Detector'),
        ('GAS_LEVEL', 'Gas Level Monitor'),
        ('PRESSURE', 'Pressure Sensor'),
        ('TEMPERATURE', 'Temperature Sensor'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GasReading(models.Model):
    sensor = models.ForeignKey(GasSensor, on_delete=models.CASCADE)
    gas_level = models.FloatField(null=True, blank=True)  # Percentage
    pressure = models.FloatField(null=True, blank=True)   # PSI
    temperature = models.FloatField(null=True, blank=True) # Celsius
    flow_rate = models.FloatField(null=True, blank=True)   # L/h
    leak_detected = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

class GasAlert(models.Model):
    ALERT_TYPES = [
        ('LEAK_DETECTED', 'Gas Leak Detected'),
        ('LOW_LEVEL', 'Low Gas Level'),
        ('HIGH_PRESSURE', 'High Pressure'),
        ('MAINTENANCE_DUE', 'Maintenance Due'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor = models.ForeignKey(GasSensor, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

# Pipeline Health Models
class PipelineSection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)
    health_percentage = models.FloatField(default=100.0)
    last_inspection = models.DateTimeField(null=True, blank=True)
    next_inspection = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ])

class MaintenanceSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=[
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ])
    is_completed = models.BooleanField(default=False)

# Regulator Models
class GasRegulator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    regulator_id = models.CharField(max_length=100)
    is_on = models.BooleanField(default=True)
    auto_mode = models.BooleanField(default=True)
    current_pressure = models.FloatField(default=0.0)
    flow_rate = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

# Emergency Contacts
class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    relationship = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-is_primary', 'name']
