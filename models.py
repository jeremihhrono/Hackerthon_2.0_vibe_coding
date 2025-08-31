from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model with role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='chw')  # admin, doctor, chw
    county = db.Column(db.String(100))
    subcounty = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    facility_name = db.Column(db.String(200))
    license_number = db.Column(db.String(50))  # For doctors
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    patients = db.relationship('Patient', backref='assigned_chw', lazy=True)
    outreach_events = db.relationship('OutreachEvent', backref='organizer', lazy=True)
    payments_made = db.relationship('Payment', foreign_keys='Payment.paid_by_id', backref='payer', lazy=True)
    payments_received = db.relationship('Payment', foreign_keys='Payment.received_by_id', backref='receiver', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role):
        return self.role == role

    def can_access_admin(self):
        return self.role == 'admin'

    def can_manage_patients(self):
        return self.role in ['admin', 'doctor', 'chw']

class Patient(db.Model):
    """FHIR-inspired Patient model"""
    id = db.Column(db.Integer, primary_key=True)
    # FHIR Patient identifiers
    patient_number = db.Column(db.String(50), unique=True, nullable=False)
    national_id = db.Column(db.String(20), unique=True)
    nhif_number = db.Column(db.String(20))
    
    # Demographics
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # male, female, other
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Address (FHIR Address)
    county = db.Column(db.String(100))
    subcounty = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    village = db.Column(db.String(100))
    address_line = db.Column(db.Text)
    
    # Healthcare specific
    blood_group = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    
    # System fields
    assigned_chw_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='active')  # active, inactive, deceased
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = db.relationship('HealthRecord', backref='patient', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='patient', lazy=True)
    event_attendances = db.relationship('EventAttendance', backref='patient', lazy=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class HealthRecord(db.Model):
    """FHIR-inspired health record/encounter"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    encounter_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    encounter_type = db.Column(db.String(50), nullable=False)  # consultation, screening, vaccination, etc.
    
    # Vital signs
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    temperature = db.Column(db.Float)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    pulse_rate = db.Column(db.Integer)
    
    # Clinical notes
    chief_complaint = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    medications_prescribed = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    
    # Provider information
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    facility_name = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OutreachEvent(db.Model):
    """Community outreach events and campaigns"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)  # vaccination, screening, education, etc.
    
    # Schedule
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    
    # Geographic targeting
    target_county = db.Column(db.String(100))
    target_subcounty = db.Column(db.String(100))
    target_ward = db.Column(db.String(100))
    
    # Capacity and targeting
    max_participants = db.Column(db.Integer)
    target_age_min = db.Column(db.Integer)
    target_age_max = db.Column(db.Integer)
    target_gender = db.Column(db.String(10))  # male, female, all
    
    # Organization
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='planned')  # planned, ongoing, completed, cancelled
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendances = db.relationship('EventAttendance', backref='event', lazy=True, cascade='all, delete-orphan')

    def get_attendance_count(self):
        return len(self.attendances)

    def is_full(self):
        if self.max_participants:
            return self.get_attendance_count() >= self.max_participants
        return False

class EventAttendance(db.Model):
    """Track patient attendance at outreach events"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('outreach_event.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    attendance_date = db.Column(db.DateTime, default=datetime.utcnow)
    services_received = db.Column(db.Text)  # JSON string of services
    notes = db.Column(db.Text)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    """Payment transactions for patient fees and CHW allowances"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Payment identifiers
    payment_reference = db.Column(db.String(100), unique=True, nullable=False)
    intasend_ref = db.Column(db.String(100))  # IntaSend transaction reference
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KES')
    payment_type = db.Column(db.String(50), nullable=False)  # patient_fee, chw_allowance, consultation_fee
    description = db.Column(db.Text)
    
    # Parties involved
    paid_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Who initiated the payment
    received_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Who received the payment
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))  # Related patient (if applicable)
    
    # Payment status
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(50))  # mpesa, card, bank_transfer
    
    # IntaSend specific fields
    intasend_checkout_id = db.Column(db.String(100))
    intasend_status = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))  # For M-Pesa payments
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def generate_reference(self):
        """Generate unique payment reference"""
        import uuid
        self.payment_reference = f"CHS{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

class AuditLog(db.Model):
    """Audit trail for security and compliance"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # patient, user, payment, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON string with additional details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
