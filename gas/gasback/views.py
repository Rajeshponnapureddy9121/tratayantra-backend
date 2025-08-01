from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # Add this import
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import RegisterSerializer, LoginSerializer
from .models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# gasback/views.py (add to existing file)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import random
from .models import EmergencyContact
from .serializer import EmergencyContactSerializer
# Add these imports to the top of your views.py if not already present
from django.db import models
from .models import *  # This should import all your models
from .serializer import *  # This should import all your serializers

regulator_state = "off" 

class SensorDataView(APIView):
    def post(self, request):
        gas = request.data.get('gas')
        fire = request.data.get('fire')
        device_id = request.data.get('device_id')
        
        print(f"Gas: {gas}, Fire: {fire}, From: {device_id}")
        # Optionally save to DB

        return Response({"message": "Data received"}, status=status.HTTP_200_OK)
    
@csrf_exempt
def sensor_data_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print("Received sensor data:", data)

        # You can save this to DB or trigger alerts here
        return JsonResponse({"message": "Data received"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


def regulator_status_view(request):
    return JsonResponse({"state": regulator_state})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensor_data(request):
    # Return mock or real sensor data
    data = {
        "gas": 45,
        "fire": 0,
        "temperature": 23.5,
        "humidity": 37,
        "device_id": "esp32_001",
        "timestamp": "2025-07-29T10:00:00Z",
        "status": "normal"
    }
    return Response({"success": 1, "data": data})

@method_decorator(csrf_exempt, name='dispatch')
class SensorDataView(APIView):
    def post(self, request):
        """Receive sensor data from ESP32"""
        try:
            gas = request.data.get('gas')
            fire = request.data.get('fire')
            device_id = request.data.get('device_id')
            temperature = request.data.get('temperature', 0)
            humidity = request.data.get('humidity', 0)
            
            print(f"Received sensor data - Gas: {gas}, Fire: {fire}, Temp: {temperature}, Humidity: {humidity}, From: {device_id}")
            
            # Here you can save to database if needed
            # For now, we'll just acknowledge receipt
            
            return Response({
                "success": 1,
                "message": "Sensor data received successfully",
                "data": {
                    "gas": gas,
                    "fire": fire,
                    "temperature": temperature,
                    "humidity": humidity,
                    "device_id": device_id
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": 0,
                "message": f"Error processing sensor data: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get latest sensor data for Android app"""
        try:
            # Mock data for now - you can replace with actual database query
            sensor_data = {
                "gas": 150,  # ppm
                "fire": 0,   # 0 = no fire, 1 = fire detected
                "temperature": 25.5,
                "humidity": 60.2,
                "device_id": "esp32_001",
                "timestamp": "2024-01-15T10:30:00Z",
                "status": "normal"  # normal, warning, danger
            }
            
            return Response({
                "success": 1,
                "message": "Sensor data retrieved successfully",
                "data": sensor_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": 0,
                "message": f"Error retrieving sensor data: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def regulator_control(request):
    """Control gas regulator from Android app"""
    try:
        data = json.loads(request.body)
        action = data.get('action')  # 'on' or 'off'
        device_id = data.get('device_id', 'esp32_001')
        
        # Here you would send command to ESP32
        print(f"Regulator control: {action} for device {device_id}")
        
        return JsonResponse({
            'success': 1,
            'message': f'Regulator turned {action} successfully',
            'data': {
                'action': action,
                'device_id': device_id,
                'status': 'executed'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': 0,
            'message': f'Error controlling regulator: {str(e)}'
        }, status=500)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def regulator_status(request):
    # TODO: Fetch actual status from GasRegulator model or hardware integration
    # For now, return mock data

    data = {
        "regulator_id": "REG_001",
        "is_on": True,
        "auto_mode": False,
        "current_pressure": 15.5,
        "flow_rate": 4.2,
        "temperature": 27.3
    }

    return Response({
        "success": 1,
        "message": "Regulator status retrieved successfully",
        "data": data
    })

@csrf_exempt
@require_http_methods(["POST"])
def add_emergency_contact(request):
    try:
        data = json.loads(request.body)
        
        # Extract data from request
        name = data.get('name')
        phone_number = data.get('phone_number')
        relationship = data.get('relationship')
        is_primary = data.get('is_primary', False)
        
        # Validate required fields
        if not all([name, phone_number, relationship]):
            return JsonResponse({
                'success': 0,
                'message': 'Name, phone number, and relationship are required'
            }, status=400)
        
        # Here you would typically save to database
        # For now, returning a success response
        response_data = {
            'success': 1,
            'message': 'Emergency contact added successfully',
            'data': {
                'id': 1,  # This should be the actual ID from database
                'name': name,
                'phone_number': phone_number,
                'relationship': relationship,
                'is_primary': is_primary
            }
        }
        
        return JsonResponse(response_data, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': 0,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': 0,
            'message': f'Server error: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_emergency_contact(request, contact_id):
    try:
        # Here you would typically delete from database
        # For now, returning a success response
        
        response_data = {
            'success': 1,
            'message': 'Emergency contact deleted successfully'
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': 0,
            'message': f'Server error: {str(e)}'
        }, status=500)
    
@csrf_exempt
def emergency_contacts(request):
    if request.method == 'GET':
        # Return list of contacts
        contacts_data = [
            {
                'id': 1,
                'name': 'John Doe',
                'phone_number': '+1234567890',
                'relationship': 'Family',
                'is_primary': True
            }
        ]
        return JsonResponse({
            'success': 1,
            'message': 'Emergency contacts retrieved successfully',
            'data': contacts_data
        })
    
    elif request.method == 'POST':
        # Add new contact
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone_number = data.get('phone_number')
            relationship = data.get('relationship')
            is_primary = data.get('is_primary', False)
            
            if not all([name, phone_number, relationship]):
                return JsonResponse({
                    'success': 0,
                    'message': 'Name, phone number, and relationship are required'
                }, status=400)
            
            # Save to database here
            response_data = {
                'success': 1,
                'message': 'Emergency contact added successfully'
            }
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': 0,
                'message': 'Invalid JSON data'
            }, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Get dashboard data for home screen"""
    try:
        user = request.user
        
        # Mock data for dashboard (replace with real sensor data later)
        dashboard_data = {
            'total_sensors': 4,
            'active_alerts': random.randint(0, 3),
            'latest_reading': {
                'gas_level': random.uniform(70, 95),
                'temperature': random.uniform(20, 30),
                'pressure': random.uniform(14, 16),
                'sensor_location': 'Kitchen',
                'timestamp': timezone.now().isoformat()
            },
            'recent_alerts': [
                {
                    'id': 1,
                    'type': 'LOW_LEVEL' if random.choice([True, False]) else 'NORMAL',
                    'message': 'Gas level check completed' if random.choice([True, False]) else 'Pressure within normal range',
                    'sensor_location': 'Kitchen',
                    'timestamp': (timezone.now() - timedelta(minutes=random.randint(5, 120))).isoformat(),
                    'is_acknowledged': random.choice([True, False])
                }
            ],
            'sensor_status': [
                {
                    'sensor_id': 'SENSOR_001',
                    'name': 'Kitchen Sensor',
                    'location': 'Kitchen',
                    'is_online': True,
                    'last_reading': timezone.now().isoformat(),
                    'gas_level': random.randint(70, 95)
                },
                {
                    'sensor_id': 'SENSOR_002', 
                    'name': 'Living Room Sensor',
                    'location': 'Living Room',
                    'is_online': True,
                    'last_reading': timezone.now().isoformat(),
                    'gas_level': random.randint(70, 95)
                }
            ],
            'regulator_status': {
                'pressure': random.uniform(14, 16),
                'is_on': True,
                'auto_mode': True,
                'flow_rate': random.uniform(2.0, 3.0),
                'temperature': random.uniform(20, 30)
            },
            'user_name': user.username,
            'last_updated': timezone.now().isoformat()
        }
        
        return Response({
            'success': 1,
            'data': dashboard_data
        })
        
    except Exception as e:
        return Response({
            'success': 0,
            'message': f'Error fetching dashboard data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    """Upload and save profile image"""
    try:
        import base64
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        import uuid
        
        image_data = request.data.get('image_data')
        if not image_data:
            return Response({
                'success': 0,
                'message': 'No image data provided'
            }, status=400)
        
        # Decode base64 image
        try:
            image_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_binary = base64.b64decode(image_data)
        except Exception as e:
            return Response({
                'success': 0,
                'message': 'Invalid image data'
            }, status=400)
        
        # Generate unique filename
        filename = f"profile_images/{request.user.id}_{uuid.uuid4().hex}.jpg"
        
        # Save image
        image_file = ContentFile(image_binary, filename)
        saved_path = default_storage.save(filename, image_file)
        
        # Get or create user profile
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.profile_image = f"/media/{saved_path}"
            profile.save()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=request.user,
                device_unique_code=f'DEV_{request.user.id}',
                profile_image=f"/media/{saved_path}"
            )
        
        return Response({
            'success': 1,
            'message': 'Profile image uploaded successfully',
            'data': {
                'image_url': f"/media/{saved_path}"
            }
        })
        
    except Exception as e:
        return Response({
            'success': 0,
            'message': f'Error uploading image: {str(e)}'
        }, status=500)


# Add other missing API functions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gas_leak_status(request):
    """Get current gas leak detection status"""
    try:
        gas_data = {
            'status': 'SAFE' if random.choice([True, True, True, False]) else 'LEAK_DETECTED',
            'gas_level': random.uniform(0, 100),
            'sensor_count': 4,
            'last_scan': timezone.now().isoformat()
        }
        
        return Response({
            'success': 1,
            'data': gas_data
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_gas_scan(request):
    """Trigger a new gas leak scan"""
    try:
        scan_result = {
            'scan_id': random.randint(1000, 9999),
            'gas_level': random.uniform(0, 100),
            'leak_detected': random.choice([True, False]),
            'scan_duration': 30,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response({
            'success': 1,
            'data': scan_result
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gas_level_data(request):
    """Get gas level monitoring data"""
    try:
        current_level = random.uniform(60, 95)
        gas_data = {
            'current_level': current_level,
            'estimated_hours': random.uniform(20, 50),
            'flow_rate': random.uniform(2.0, 3.0),
            'pressure': random.uniform(14, 16),
            'recent_readings': [
                {
                    'time': f"{(timezone.now() - timedelta(minutes=i*30)).strftime('%H:%M')}",
                    'level': current_level + random.uniform(-5, 5),
                    'status': 'Good'
                } for i in range(5)
            ]
        }
        
        return Response({
            'success': 1,
            'data': gas_data
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_health_data(request):
    """Get pipeline health monitoring data"""
    try:
        pipeline_data = {
            'overall_health': round(random.uniform(75, 95), 1),
            'sections': [
                {
                    'section_name': 'Main Line A',
                    'health_percentage': round(random.uniform(85, 95), 1),
                    'status': 'Excellent',
                    'last_inspection': timezone.now().date().isoformat()  # Just date, not full timestamp
                },
                {
                    'section_name': 'Kitchen Branch',
                    'health_percentage': round(random.uniform(80, 90), 1),
                    'status': 'Good',
                    'last_inspection': timezone.now().date().isoformat()
                },
                {
                    'section_name': 'Distribution Line C',
                    'health_percentage': round(random.uniform(65, 85), 1),
                    'status': 'Needs Attention',
                    'last_inspection': (timezone.now() - timedelta(days=7)).date().isoformat()
                }
            ],
            'maintenance_schedule': [
                {
                    'title': 'Pressure Test - Main Line A',
                    'description': 'Routine pressure testing and safety inspection',
                    'scheduled_date': (timezone.now() + timedelta(days=15)).date().isoformat(),
                    'priority': 'MEDIUM'
                },
                {
                    'title': 'Leak Detection Scan',
                    'description': 'Comprehensive leak detection for all sections',
                    'scheduled_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
                    'priority': 'HIGH'
                }
            ]
        }
        
        return Response({
            'success': 1,
            'message': 'Pipeline health data retrieved successfully',
            'data': pipeline_data
        })
    except Exception as e:
        return Response({
            'success': 0, 
            'message': f'Error retrieving pipeline health data: {str(e)}'
        }, status=500)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def regulator_control(request):
    """Get or control regulator settings"""
    try:
        if request.method == 'GET':
            regulator_data = {
                'regulator_id': f'REG_{request.user.id}',
                'is_on': True,
                'auto_mode': True,
                'current_pressure': random.uniform(14, 16),
                'flow_rate': random.uniform(2.0, 3.0),
                'temperature': random.uniform(20, 30)
            }
            
            return Response({
                'success': 1,
                'data': regulator_data
            })
        
        elif request.method == 'POST':
            # Handle regulator control actions
            action = request.data.get('action', '')
            
            regulator_data = {
                'regulator_id': f'REG_{request.user.id}',
                'is_on': action != 'turn_off',
                'auto_mode': action != 'manual_mode',
                'current_pressure': random.uniform(14, 16),
                'flow_rate': random.uniform(2.0, 3.0),
                'temperature': random.uniform(20, 30)
            }
            
            return Response({
                'success': 1,
                'message': f'Regulator {action} completed',
                'data': regulator_data
            })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def emergency_contacts(request):
    """Get or add emergency contacts"""
    try:
        if request.method == 'GET':
            # Mock emergency contacts
            contacts = [
                {
                    'id': 1,
                    'name': 'Emergency Services',
                    'phone_number': '911',
                    'relationship': 'Emergency Service',
                    'is_primary': True
                },
                {
                    'id': 2,
                    'name': 'John Doe',
                    'phone_number': '+1234567890',
                    'relationship': 'Family',
                    'is_primary': False
                }
            ]
            
            return Response({
                'success': 1,
                'data': contacts
            })
        
        elif request.method == 'POST':
            # Add new contact (mock response)
            new_contact = {
                'id': random.randint(100, 999),
                'name': request.data.get('name'),
                'phone_number': request.data.get('phone_number'),
                'relationship': request.data.get('relationship'),
                'is_primary': request.data.get('is_primary', False)
            }
            
            return Response({
                'success': 1,
                'message': 'Contact added successfully',
                'data': new_contact
            })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_emergency_contact(request, contact_id):
    """Delete emergency contact"""
    try:
        return Response({
            'success': 1,
            'message': 'Contact deleted successfully'
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_emergency_sos(request):
    """Trigger emergency SOS call"""
    try:
        sos_data = {
            'sos_id': random.randint(10000, 99999),
            'triggered_at': timezone.now().isoformat(),
            'contacts_called': 2,
            'estimated_response_time': '5-10 minutes'
        }
        
        return Response({
            'success': 1,
            'message': 'Emergency SOS triggered successfully',
            'data': sos_data
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile_management(request):
    """Get or update user profile"""
    try:
        if request.method == 'GET':
            try:
                profile = UserProfile.objects.get(user=request.user)
                device_code = profile.device_unique_code
            except UserProfile.DoesNotExist:
                device_code = f'DEV_{request.user.id}'
            
            return Response({
                'success': 1,
                'data': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'phone_number': getattr(profile, 'phone_number', None) if 'profile' in locals() else None,
                    'profile_image': None,
                    'device_unique_code': device_code
                }
            })
        
        elif request.method == 'PUT':
            # Update user profile
            user_data = request.data
            if 'username' in user_data:
                request.user.username = user_data['username']
            if 'email' in user_data:
                request.user.email = user_data['email']
            request.user.save()
            
            return Response({
                'success': 1,
                'message': 'Profile updated successfully'
            })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

# Gas Leak Detection APIs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gas_leak_status(request):
    """Get current gas leak detection status"""
    try:
        # Get latest gas leak sensor readings
        leak_sensors = GasSensor.objects.filter(
            user=request.user,
            sensor_type='GAS_LEAK',
            is_active=True
        )
        
        overall_status = "SAFE"
        gas_level = 0
        
        if leak_sensors.exists():
            latest_reading = GasReading.objects.filter(
                sensor__in=leak_sensors
            ).order_by('-timestamp').first()
            
            if latest_reading:
                gas_level = random.uniform(0, 100)  # Simulate sensor data
                overall_status = "LEAK_DETECTED" if latest_reading.leak_detected else "SAFE"
        
        return Response({
            'success': 1,
            'data': {
                'status': overall_status,
                'gas_level': gas_level,
                'sensor_count': leak_sensors.count(),
                'last_scan': timezone.now().isoformat()
            }
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_gas_scan(request):
    """Trigger a new gas leak scan"""
    try:
        # Simulate scanning process
        scan_result = {
            'scan_id': random.randint(1000, 9999),
            'gas_level': random.uniform(0, 100),
            'leak_detected': random.choice([True, False]),
            'scan_duration': 30,  # seconds
            'timestamp': timezone.now().isoformat()
        }
        
        # If leak detected, create alert
        if scan_result['leak_detected']:
            sensor = GasSensor.objects.filter(
                user=request.user,
                sensor_type='GAS_LEAK'
            ).first()
            
            if sensor:
                GasAlert.objects.create(
                    user=request.user,
                    sensor=sensor,
                    alert_type='LEAK_DETECTED',
                    message=f'Gas leak detected with level {scan_result["gas_level"]:.1f}%'
                )
        
        return Response({
            'success': 1,
            'data': scan_result
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)
    

# Add this to your gasback/views.py file

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Get dashboard data for home screen"""
    try:
        user = request.user
        
        # Get user's sensors
        sensors = GasSensor.objects.filter(user=user, is_active=True)
        total_sensors = sensors.count()
        
        # Get active alerts
        active_alerts = GasAlert.objects.filter(
            user=user,
            is_acknowledged=False
        ).count()
        
        # Get latest reading
        latest_reading = None
        if sensors.exists():
            latest_reading_obj = GasReading.objects.filter(
                sensor__user=user
            ).order_by('-timestamp').first()
            
            if latest_reading_obj:
                latest_reading = {
                    'gas_level': latest_reading_obj.gas_level,
                    'temperature': latest_reading_obj.temperature,
                    'pressure': latest_reading_obj.pressure,
                    'sensor_location': latest_reading_obj.sensor.location,
                    'timestamp': latest_reading_obj.timestamp.isoformat()
                }
        
        # Get recent alerts
        recent_alerts = GasAlert.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        recent_alerts_data = []
        for alert in recent_alerts:
            recent_alerts_data.append({
                'id': alert.id,
                'type': alert.alert_type,
                'message': alert.message,
                'sensor_location': alert.sensor.location,
                'timestamp': alert.created_at.isoformat(),
                'is_acknowledged': alert.is_acknowledged
            })
        
        # Get sensor status
        sensor_status = []
        for sensor in sensors:
            latest_reading = GasReading.objects.filter(
                sensor=sensor
            ).order_by('-timestamp').first()
            
            if latest_reading:
                # Determine status based on latest reading time
                time_diff = timezone.now() - latest_reading.timestamp
                is_online = time_diff.total_seconds() < 300  # 5 minutes
                
                sensor_status.append({
                    'sensor_id': sensor.sensor_id,
                    'name': sensor.sensor_name,
                    'location': sensor.location,
                    'is_online': is_online,
                    'last_reading': latest_reading.timestamp.isoformat(),
                    'gas_level': latest_reading.gas_level or 0
                })
        
        # Get regulator status
        regulator = GasRegulator.objects.filter(user=user).first()
        regulator_status = {}
        if regulator:
            regulator_status = {
                'pressure': regulator.current_pressure,
                'is_on': regulator.is_on,
                'auto_mode': regulator.auto_mode,
                'flow_rate': regulator.flow_rate,
                'temperature': regulator.temperature
            }
        
        dashboard_data = {
            'total_sensors': total_sensors,
            'active_alerts': active_alerts,
            'latest_reading': latest_reading,
            'recent_alerts': recent_alerts_data,
            'sensor_status': sensor_status,
            'regulator_status': regulator_status,
            'user_name': user.username,
            'last_updated': timezone.now().isoformat()
        }
        
        return Response({
            'success': 1,
            'data': dashboard_data
        })
        
    except Exception as e:
        return Response({
            'success': 0,
            'message': f'Error fetching dashboard data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gas_level_data(request):
    """Get gas level monitoring data"""
    try:
        gas_data = {
            'current_level': round(random.uniform(60, 90), 1),
            'estimated_hours': round(random.uniform(20, 50), 1),
            'flow_rate': round(random.uniform(2.0, 4.0), 1),
            'pressure': round(random.uniform(12.0, 18.0), 1),
            'recent_readings': [
                {
                    'time': '10:30 AM',
                    'level': 0.75,
                    'status': 'Normal'
                },
                {
                    'time': '09:30 AM',
                    'level': 0.77,
                    'status': 'Normal'
                },
                {
                    'time': '08:30 AM',
                    'level': 0.79,
                    'status': 'Normal'
                }
            ]
        }
        
        return Response({
            'success': 1,
            'message': 'Gas level data retrieved successfully',
            'data': gas_data
        })
    except Exception as e:
        return Response({
            'success': 0, 
            'message': f'Error retrieving gas level data: {str(e)}'
        }, status=500)



# Gas Level Monitoring APIs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gas_level_data(request):
    """Get gas level monitoring data"""
    try:
        level_sensors = GasSensor.objects.filter(
            user=request.user,
            sensor_type='GAS_LEVEL',
            is_active=True
        )
        
        current_level = random.uniform(60, 95)  # Simulate gas level
        estimated_hours = random.uniform(20, 50)
        
        # Recent readings simulation
        recent_readings = []
        for i in range(5):
            time_offset = i * 30  # 30 minutes apart
            reading_time = timezone.now() - timedelta(minutes=time_offset)
            recent_readings.append({
                'time': reading_time.strftime('%H:%M'),
                'level': current_level + random.uniform(-5, 5),
                'status': 'Good'
            })
        
        return Response({
            'success': 1,
            'data': {
                'current_level': current_level,
                'estimated_hours': estimated_hours,
                'flow_rate': random.uniform(2.0, 3.0),
                'pressure': random.uniform(14, 16),
                'recent_readings': recent_readings
            }
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

# Pipeline Health APIs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_health_data(request):
    """Get pipeline health monitoring data"""
    try:
        sections = PipelineSection.objects.filter(user=request.user)
        
        if not sections.exists():
            # Create default sections
            default_sections = [
                {'section_name': 'Main Line', 'health_percentage': 92, 'status': 'EXCELLENT'},
                {'section_name': 'Kitchen', 'health_percentage': 88, 'status': 'GOOD'},
                {'section_name': 'Water Heater', 'health_percentage': 75, 'status': 'FAIR'},
                {'section_name': 'Outdoor', 'health_percentage': 95, 'status': 'EXCELLENT'},
            ]
            
            for section_data in default_sections:
                PipelineSection.objects.create(
                    user=request.user,
                    **section_data,
                    last_inspection=timezone.now() - timedelta(hours=random.randint(1, 24))
                )
            
            sections = PipelineSection.objects.filter(user=request.user)
        
        overall_health = sections.aggregate(avg_health=models.Avg('health_percentage'))['avg_health'] or 0
        
        maintenance_items = MaintenanceSchedule.objects.filter(
            user=request.user,
            is_completed=False,
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:3]
        
        return Response({
            'success': 1,
            'data': {
                'overall_health': overall_health,
                'sections': PipelineSectionSerializer(sections, many=True).data,
                'maintenance_schedule': MaintenanceScheduleSerializer(maintenance_items, many=True).data
            }
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

# Regulator Control APIs
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def regulator_control(request):
    """Get or control regulator settings"""
    try:
        regulator, created = GasRegulator.objects.get_or_create(
            user=request.user,
            defaults={
                'regulator_id': f'REG_{request.user.id}',
                'is_on': True,
                'auto_mode': True,
                'current_pressure': 15.2,
                'flow_rate': 2.5,
                'temperature': 22.5
            }
        )
        
        if request.method == 'GET':
            return Response({
                'success': 1,
                'data': GasRegulatorSerializer(regulator).data
            })
        
        elif request.method == 'POST':
            action = request.data.get('action')
            
            if action == 'toggle_power':
                regulator.is_on = not regulator.is_on
            elif action == 'toggle_auto':
                regulator.auto_mode = not regulator.auto_mode
            elif action == 'update_settings':
                serializer = GasRegulatorSerializer(regulator, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'success': 1, 'message': 'Settings updated'})
                return Response({'success': 0, 'errors': serializer.errors}, status=400)
            
            regulator.save()
            return Response({
                'success': 1,
                'message': f'Regulator {action} completed',
                'data': GasRegulatorSerializer(regulator).data
            })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)
    

# Emergency Contacts APIs
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def emergency_contacts(request):
    """Get or add emergency contacts"""
    try:
        if request.method == 'GET':
            contacts = EmergencyContact.objects.filter(user=request.user, is_active=True)
            return Response({
                'success': 1,
                'data': EmergencyContactSerializer(contacts, many=True).data
            })
        
        elif request.method == 'POST':
            serializer = EmergencyContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({
                    'success': 1,
                    'message': 'Contact added successfully',
                    'data': serializer.data
                })
            return Response({'success': 0, 'errors': serializer.errors}, status=400)
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)
    


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def emergency_contacts_management(request):
    if request.method == 'GET':
        try:
            contacts = EmergencyContact.objects.filter(user=request.user)
            contacts_data = [{
                'id': c.id,
                'name': c.name,
                'phone_number': c.phone_number,
                'relationship': c.relationship,
                'is_primary': c.is_primary,
            } for c in contacts]
            return Response({'success': 1, 'data': contacts_data})
        except Exception as e:
            return Response({'success': 0, 'message': f'Error loading contacts: {str(e)}'}, status=500)
    elif request.method == 'POST':
        try:
            new_contact = EmergencyContact.objects.create(
                user=request.user,
                name=request.data.get('name'),
                phone_number=request.data.get('phone_number'),
                relationship=request.data.get('relationship', "Emergency Contact"),
                is_primary=request.data.get('is_primary', False)
            )
            return Response({'success': 1, 'message': 'Contact added successfully'})
        except Exception as e:
            return Response({'success': 0, 'message': f'Error adding contact: {str(e)}'}, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_emergency_contact(request, contact_id):
    """Delete emergency contact"""
    try:
        contact = EmergencyContact.objects.get(id=contact_id, user=request.user)
        contact.is_active = False
        contact.save()
        return Response({'success': 1, 'message': 'Contact deleted'})
    except EmergencyContact.DoesNotExist:
        return Response({'success': 0, 'message': 'Contact not found'}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_emergency_contact(request, contact_id):
    """
    Update an existing emergency contact by ID.
    """
    try:
        # Fetch the emergency contact belonging to the logged-in user
        contact = EmergencyContact.objects.get(id=contact_id, user=request.user, is_active=True)
    except EmergencyContact.DoesNotExist:
        return Response(
            {"success": 0, "message": "Contact not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Deserialize incoming data to update the contact
    serializer = EmergencyContactSerializer(contact, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()  # Save updated contact
        return Response(
            {"success": 1, "message": "Contact updated successfully.", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"success": 0, "message": "Validation error.", "errors": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_emergency_sos(request):
    """Trigger emergency SOS call"""
    try:
        # Get all active emergency contacts
        contacts = EmergencyContact.objects.filter(user=request.user, is_active=True)
        
        if not contacts.exists():
            return Response({
                'success': 0,
                'message': 'No emergency contacts found'
            }, status=400)
        
        # Simulate emergency call process
        sos_data = {
            'sos_id': random.randint(10000, 99999),
            'triggered_at': timezone.now().isoformat(),
            'contacts_called': contacts.count(),
            'estimated_response_time': '5-10 minutes'
        }
        
        return Response({
            'success': 1,
            'message': 'Emergency SOS triggered successfully',
            'data': sos_data
        })
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)

# Profile Management APIs
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile_management(request):
    """Get or update user profile"""
    try:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'device_unique_code': f'DEV_{request.user.id}'}
        )
        
        if request.method == 'GET':
            return Response({
                'success': 1,
                'data': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'phone_number': profile.phone_number,
                    'profile_image': profile.profile_image,
                    'device_unique_code': profile.device_unique_code,
                    'notification_preferences': profile.notification_preferences
                }
            })
        
        elif request.method == 'PUT':
            # Update user fields
            user_data = request.data
            if 'username' in user_data:
                request.user.username = user_data['username']
            if 'email' in user_data:
                request.user.email = user_data['email']
            request.user.save()
            
            # Update profile fields
            serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': 1,
                    'message': 'Profile updated successfully'
                })
            return Response({'success': 0, 'errors': serializer.errors}, status=400)
    except Exception as e:
        return Response({'success': 0, 'message': str(e)}, status=500)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Fetch phone number for response
            profile = UserProfile.objects.get(user=user)
            return Response({
                "success": 1,
                "message": "User registered successfully!",
                "phone_number": profile.phone_number
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": 0,
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            try:
                user_profile = UserProfile.objects.get(user=user)
                device_unique_code = user_profile.device_unique_code
                phone_number = user_profile.phone_number
            except UserProfile.DoesNotExist:
                device_unique_code = None
                phone_number = None
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": phone_number,
                    # add other fields if you want
                },
                "access_token": str(refresh.access_token),   # <-- Fix: use access_token in key!
                "refresh_token": str(refresh),               # <-- Fix: use refresh_token in key!
                "message": "Login successful!",
            }, status=status.HTTP_200_OK)
        return Response({
            "success": 0,
            "message": "Login failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class SimpleView(APIView):
    def get(self, request):
        return Response({"message": "This is a simple view!"}, status=status.HTTP_200_OK)
    
    def post(self, request):
        return Response({"message": "This is a simple POST view!"}, status=status.HTTP_201_CREATED)
