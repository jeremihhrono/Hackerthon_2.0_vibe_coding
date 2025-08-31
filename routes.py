import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Patient, HealthRecord, OutreachEvent, EventAttendance, Payment, AuditLog
from forms import LoginForm, RegistrationForm, PatientForm, HealthRecordForm, OutreachEventForm, PaymentForm
from utils import log_audit, generate_patient_number, create_intasend_checkout
from functools import wraps

def role_required(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_role(role):
                flash('Access denied. Insufficient privileges.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_access_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            log_audit('user_login', 'user', user.id, f'User {user.username} logged in')
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username, password, or account inactive.', 'error')
            log_audit('failed_login', 'user', None, f'Failed login attempt for username: {form.username.data}')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            role=form.role.data,
            county=form.county.data,
            subcounty=form.subcounty.data,
            ward=form.ward.data,
            facility_name=form.facility_name.data,
            license_number=form.license_number.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        log_audit('user_registration', 'user', user.id, f'New user registered: {user.username}')
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    log_audit('user_logout', 'user', current_user.id, f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get dashboard statistics based on user role
    stats = {}
    
    if current_user.role == 'admin':
        stats['total_users'] = User.query.filter_by(is_active=True).count()
        stats['total_patients'] = Patient.query.filter_by(status='active').count()
        stats['total_events'] = OutreachEvent.query.count()
        stats['pending_payments'] = Payment.query.filter_by(status='pending').count()
    elif current_user.role == 'doctor':
        stats['my_patients'] = Patient.query.filter_by(assigned_chw_id=current_user.id, status='active').count()
        stats['recent_consultations'] = HealthRecord.query.filter_by(provider_id=current_user.id).filter(
            HealthRecord.encounter_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
    elif current_user.role == 'chw':
        stats['my_patients'] = Patient.query.filter_by(assigned_chw_id=current_user.id, status='active').count()
        stats['my_events'] = OutreachEvent.query.filter_by(organizer_id=current_user.id).count()
        stats['pending_allowances'] = Payment.query.filter_by(
            received_by_id=current_user.id, 
            payment_type='chw_allowance', 
            status='pending'
        ).count()
    
    # Recent activities
    recent_events = OutreachEvent.query.filter(
        OutreachEvent.start_date >= datetime.utcnow()
    ).order_by(OutreachEvent.start_date).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, recent_events=recent_events)

@app.route('/patients')
@login_required
def patients():
    """Patient list"""
    if not current_user.can_manage_patients():
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Patient.query.filter_by(status='active')
    
    # Role-based filtering
    if current_user.role == 'chw':
        query = query.filter_by(assigned_chw_id=current_user.id)
    
    # Search functionality
    if search:
        query = query.filter(
            (Patient.first_name.contains(search)) |
            (Patient.last_name.contains(search)) |
            (Patient.patient_number.contains(search)) |
            (Patient.national_id.contains(search))
        )
    
    patients = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('patients.html', patients=patients, search=search)

@app.route('/patients/new', methods=['GET', 'POST'])
@login_required
def new_patient():
    """Create new patient"""
    if not current_user.can_manage_patients():
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(
            patient_number=generate_patient_number(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            national_id=form.national_id.data,
            nhif_number=form.nhif_number.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            county=form.county.data,
            subcounty=form.subcounty.data,
            ward=form.ward.data,
            village=form.village.data,
            address_line=form.address_line.data,
            blood_group=form.blood_group.data,
            allergies=form.allergies.data,
            chronic_conditions=form.chronic_conditions.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            assigned_chw_id=current_user.id if current_user.role == 'chw' else None
        )
        
        db.session.add(patient)
        db.session.commit()
        
        log_audit('patient_created', 'patient', patient.id, f'New patient created: {patient.get_full_name()}')
        flash(f'Patient {patient.get_full_name()} has been registered successfully.', 'success')
        return redirect(url_for('patient_detail', id=patient.id))
    
    return render_template('patient_detail.html', form=form, patient=None)

@app.route('/patients/<int:id>')
@login_required
def patient_detail(id):
    """Patient detail view"""
    patient = Patient.query.get_or_404(id)
    
    # Role-based access control
    if current_user.role == 'chw' and patient.assigned_chw_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('patients'))
    
    # Get patient's health records
    health_records = HealthRecord.query.filter_by(patient_id=patient.id).order_by(
        HealthRecord.encounter_date.desc()
    ).limit(10).all()
    
    # Get recent payments
    payments = Payment.query.filter_by(patient_id=patient.id).order_by(
        Payment.created_at.desc()
    ).limit(5).all()
    
    return render_template('patient_detail.html', patient=patient, health_records=health_records, payments=payments)

@app.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    """Edit patient information"""
    patient = Patient.query.get_or_404(id)
    
    # Role-based access control
    if current_user.role == 'chw' and patient.assigned_chw_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('patients'))
    
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        form.populate_obj(patient)
        patient.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit('patient_updated', 'patient', patient.id, f'Patient updated: {patient.get_full_name()}')
        flash('Patient information updated successfully.', 'success')
        return redirect(url_for('patient_detail', id=patient.id))
    
    return render_template('patient_detail.html', form=form, patient=patient)

@app.route('/patients/<int:id>/health_record', methods=['GET', 'POST'])
@login_required
def new_health_record(id):
    """Create new health record for patient"""
    patient = Patient.query.get_or_404(id)
    
    # Role-based access control
    if current_user.role == 'chw' and patient.assigned_chw_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('patients'))
    
    form = HealthRecordForm()
    if form.validate_on_submit():
        health_record = HealthRecord(
            patient_id=patient.id,
            encounter_type=form.encounter_type.data,
            weight=form.weight.data,
            height=form.height.data,
            temperature=form.temperature.data,
            blood_pressure_systolic=form.blood_pressure_systolic.data,
            blood_pressure_diastolic=form.blood_pressure_diastolic.data,
            pulse_rate=form.pulse_rate.data,
            chief_complaint=form.chief_complaint.data,
            diagnosis=form.diagnosis.data,
            treatment_plan=form.treatment_plan.data,
            medications_prescribed=form.medications_prescribed.data,
            follow_up_date=form.follow_up_date.data,
            provider_id=current_user.id,
            facility_name=form.facility_name.data or current_user.facility_name
        )
        
        db.session.add(health_record)
        db.session.commit()
        
        log_audit('health_record_created', 'health_record', health_record.id, 
                 f'Health record created for patient: {patient.get_full_name()}')
        flash('Health record added successfully.', 'success')
        return redirect(url_for('patient_detail', id=patient.id))
    
    return render_template('patient_detail.html', form=form, patient=patient, add_record=True)

@app.route('/outreach')
@login_required
def outreach():
    """Outreach events list"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = OutreachEvent.query
    
    # Role-based filtering
    if current_user.role == 'chw':
        query = query.filter_by(organizer_id=current_user.id)
    
    # Status filtering
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    events = query.order_by(OutreachEvent.start_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('outreach.html', events=events, status_filter=status_filter)

@app.route('/outreach/new', methods=['GET', 'POST'])
@login_required
def new_outreach():
    """Create new outreach event"""
    form = OutreachEventForm()
    if form.validate_on_submit():
        event = OutreachEvent(
            title=form.title.data,
            description=form.description.data,
            event_type=form.event_type.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            target_county=form.target_county.data,
            target_subcounty=form.target_subcounty.data,
            target_ward=form.target_ward.data,
            max_participants=form.max_participants.data,
            target_age_min=form.target_age_min.data,
            target_age_max=form.target_age_max.data,
            target_gender=form.target_gender.data,
            organizer_id=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        log_audit('outreach_event_created', 'outreach_event', event.id, f'Outreach event created: {event.title}')
        flash('Outreach event created successfully.', 'success')
        return redirect(url_for('outreach_detail', id=event.id))
    
    return render_template('outreach_detail.html', form=form, event=None)

@app.route('/outreach/<int:id>')
@login_required
def outreach_detail(id):
    """Outreach event detail"""
    event = OutreachEvent.query.get_or_404(id)
    
    # Get attendances
    attendances = EventAttendance.query.filter_by(event_id=event.id).all()
    
    return render_template('outreach_detail.html', event=event, attendances=attendances)

@app.route('/outreach/<int:id>/attend', methods=['POST'])
@login_required
def record_attendance(id):
    """Record patient attendance at outreach event"""
    event = OutreachEvent.query.get_or_404(id)
    patient_id = request.form.get('patient_id')
    services = request.form.get('services', '')
    notes = request.form.get('notes', '')
    
    if not patient_id:
        flash('Please select a patient.', 'error')
        return redirect(url_for('outreach_detail', id=id))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if already attended
    existing = EventAttendance.query.filter_by(event_id=event.id, patient_id=patient_id).first()
    if existing:
        flash('Patient has already been recorded for this event.', 'warning')
        return redirect(url_for('outreach_detail', id=id))
    
    attendance = EventAttendance(
        event_id=event.id,
        patient_id=patient_id,
        services_received=services,
        notes=notes,
        recorded_by_id=current_user.id
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    log_audit('event_attendance_recorded', 'event_attendance', attendance.id, 
             f'Attendance recorded for {patient.get_full_name()} at {event.title}')
    flash(f'Attendance recorded for {patient.get_full_name()}.', 'success')
    return redirect(url_for('outreach_detail', id=id))

@app.route('/payments')
@login_required
def payments():
    """Payments list"""
    page = request.args.get('page', 1, type=int)
    payment_type = request.args.get('type', 'all')
    status_filter = request.args.get('status', 'all')
    
    query = Payment.query
    
    # Role-based filtering
    if current_user.role == 'chw':
        query = query.filter(
            (Payment.paid_by_id == current_user.id) | 
            (Payment.received_by_id == current_user.id)
        )
    elif current_user.role == 'doctor':
        query = query.filter(
            (Payment.paid_by_id == current_user.id) | 
            (Payment.received_by_id == current_user.id)
        )
    
    # Type filtering
    if payment_type != 'all':
        query = query.filter_by(payment_type=payment_type)
    
    # Status filtering
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('payments.html', payments=payments, 
                         payment_type=payment_type, status_filter=status_filter)

@app.route('/payments/new', methods=['GET', 'POST'])
@login_required
def new_payment():
    """Create new payment"""
    form = PaymentForm()
    patient_id = request.args.get('patient_id')
    patient = None
    
    if patient_id:
        patient = Patient.query.get_or_404(patient_id)
    
    if form.validate_on_submit():
        payment = Payment(
            amount=form.amount.data,
            payment_type=form.payment_type.data,
            description=form.description.data,
            phone_number=form.phone_number.data,
            paid_by_id=current_user.id,
            patient_id=patient.id if patient else None
        )
        payment.generate_reference()
        
        # Create IntaSend checkout (this would integrate with actual IntaSend API)
        checkout_url = create_intasend_checkout(payment)
        if checkout_url:
            payment.intasend_checkout_id = checkout_url
            db.session.add(payment)
            db.session.commit()
            
            log_audit('payment_initiated', 'payment', payment.id, 
                     f'Payment initiated: {payment.payment_reference}')
            flash('Payment initiated. You will be redirected to complete the payment.', 'success')
            return redirect(checkout_url)
        else:
            flash('Error initiating payment. Please try again.', 'error')
    
    return render_template('payment_form.html', form=form, patient=patient)

@app.route('/users')
@admin_required
def users():
    """User management (admin only)"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')
    
    query = User.query.filter_by(is_active=True)
    
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('users.html', users=users, role_filter=role_filter)

@app.route('/users/<int:id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(id):
    """Toggle user active status"""
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    log_audit('user_status_changed', 'user', user.id, f'User {user.username} {status}')
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('users'))

@app.route('/api/patients/search')
@login_required
def api_patients_search():
    """API endpoint for patient search (for AJAX)"""
    if not current_user.can_manage_patients():
        return jsonify({'error': 'Access denied'}), 403
    
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    patients_query = Patient.query.filter_by(status='active')
    
    # Role-based filtering
    if current_user.role == 'chw':
        patients_query = patients_query.filter_by(assigned_chw_id=current_user.id)
    
    patients = patients_query.filter(
        (Patient.first_name.contains(query)) |
        (Patient.last_name.contains(query)) |
        (Patient.patient_number.contains(query))
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.get_full_name(),
        'patient_number': p.patient_number,
        'age': p.get_age()
    } for p in patients])

@app.route('/webhooks/intasend', methods=['POST'])
def intasend_webhook():
    """IntaSend webhook handler"""
    try:
        data = request.get_json()
        
        # Validate webhook (you should verify the signature in production)
        invoice_id = data.get('invoice_id')
        status = data.get('state')
        
        if invoice_id and status:
            payment = Payment.query.filter_by(intasend_checkout_id=invoice_id).first()
            if payment:
                payment.intasend_status = status
                if status.lower() == 'complete':
                    payment.status = 'completed'
                    payment.completed_at = datetime.utcnow()
                elif status.lower() == 'failed':
                    payment.status = 'failed'
                
                db.session.commit()
                
                log_audit('payment_webhook', 'payment', payment.id, 
                         f'Payment webhook received: {status}')
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        app.logger.error(f'Webhook error: {str(e)}')
        return jsonify({'status': 'error'}), 400

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
