import os
import uuid
import requests
from datetime import datetime
from flask import request
from flask_login import current_user
from app import db
from models import AuditLog

def log_audit(action, resource_type, resource_id, details):
    """Log audit trail"""
    try:
        audit_log = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        # Don't let audit logging break the main functionality
        print(f"Audit logging error: {str(e)}")

def generate_patient_number():
    """Generate unique patient number"""
    prefix = "CHS"
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = str(uuid.uuid4())[:8].upper()
    return f"{prefix}{date_part}{random_part}"

def create_intasend_checkout(payment):
    """Create IntaSend checkout session"""
    try:
        # IntaSend API configuration
        api_key = os.environ.get('INTASEND_API_KEY', 'ISPubKey_test_placeholder')
        api_secret = os.environ.get('INTASEND_API_SECRET', 'ISSecKey_test_placeholder')
        base_url = os.environ.get('INTASEND_BASE_URL', 'https://sandbox.intasend.com/api/v1/')
        
        # Prepare checkout data
        checkout_data = {
            'amount': float(payment.amount),
            'currency': payment.currency,
            'email': current_user.email if current_user.is_authenticated else 'patient@example.com',
            'phone_number': payment.phone_number,
            'api_ref': payment.payment_reference,
            'comment': payment.description or f'{payment.payment_type} payment',
            'redirect_url': f'{request.host_url}payments?status=success',
            'webhook_url': f'{request.host_url}webhooks/intasend'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-IntaSend-Public-Key-Id': api_key
        }
        
        # Make API request to IntaSend
        response = requests.post(
            f'{base_url}payment/collection/',
            json=checkout_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            return result.get('url')  # Return checkout URL
        else:
            print(f"IntaSend API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"IntaSend checkout error: {str(e)}")
        # For development, return a mock URL
        return f"/payments?mock_payment={payment.payment_reference}"

def format_kenyan_phone(phone_number):
    """Format phone number to Kenyan standard"""
    if not phone_number:
        return None
    
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone_number))
    
    # Handle different formats
    if phone.startswith('254'):
        return f"+{phone}"
    elif phone.startswith('0'):
        return f"+254{phone[1:]}"
    elif len(phone) == 9:
        return f"+254{phone}"
    else:
        return f"+254{phone}"

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    if not weight or not height or height == 0:
        return None
    
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    """Get BMI category"""
    if not bmi:
        return "Unknown"
    
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def format_currency(amount):
    """Format amount as Kenyan Shillings"""
    if not amount:
        return "KES 0.00"
    return f"KES {amount:,.2f}"

def get_age_group(age):
    """Get age group for reporting"""
    if age < 1:
        return "Infant (0-1)"
    elif age < 5:
        return "Child (1-4)"
    elif age < 15:
        return "Child (5-14)"
    elif age < 25:
        return "Youth (15-24)"
    elif age < 65:
        return "Adult (25-64)"
    else:
        return "Elderly (65+)"

def validate_kenyan_id(national_id):
    """Basic validation for Kenyan National ID"""
    if not national_id:
        return False
    
    # Remove any non-digit characters
    id_number = ''.join(filter(str.isdigit, national_id))
    
    # Should be 8 digits
    return len(id_number) == 8

def get_kenyan_counties():
    """Get list of Kenyan counties"""
    return [
        'Baringo', 'Bomet', 'Bungoma', 'Busia', 'Elgeyo-Marakwet', 'Embu', 'Garissa',
        'Homa Bay', 'Isiolo', 'Kajiado', 'Kakamega', 'Kericho', 'Kiambu', 'Kilifi',
        'Kirinyaga', 'Kisii', 'Kisumu', 'Kitui', 'Kwale', 'Laikipia', 'Lamu', 'Machakos',
        'Makueni', 'Mandera', 'Marsabit', 'Meru', 'Migori', 'Mombasa', 'Murang\'a',
        'Nairobi', 'Nakuru', 'Nandi', 'Narok', 'Nyamira', 'Nyandarua', 'Nyeri',
        'Samburu', 'Siaya', 'Taita-Taveta', 'Tana River', 'Tharaka-Nithi', 'Trans Nzoia',
        'Turkana', 'Uasin Gishu', 'Vihiga', 'Wajir', 'West Pokot'
    ]
