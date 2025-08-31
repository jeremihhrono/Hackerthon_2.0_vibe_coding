from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, DateField, IntegerField, TelField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import DateInput

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone_number = TelField('Phone Number', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[
        ('chw', 'Community Health Worker'),
        ('doctor', 'Doctor/Clinician'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    county = SelectField('County', choices=[
        ('', 'Select County'),
        ('nairobi', 'Nairobi'),
        ('kiambu', 'Kiambu'),
        ('machakos', 'Machakos'),
        ('kajiado', 'Kajiado'),
        ('murang\'a', 'Murang\'a'),
        ('nyeri', 'Nyeri'),
        ('kirinyaga', 'Kirinyaga'),
        ('nyandarua', 'Nyandarua'),
        ('nakuru', 'Nakuru'),
        ('laikipia', 'Laikipia'),
        ('meru', 'Meru'),
        ('tharaka_nithi', 'Tharaka Nithi'),
        ('embu', 'Embu'),
        ('kitui', 'Kitui'),
        ('makueni', 'Makueni'),
        ('kisumu', 'Kisumu'),
        ('siaya', 'Siaya'),
        ('busia', 'Busia'),
        ('kakamega', 'Kakamega'),
        ('vihiga', 'Vihiga'),
        ('bungoma', 'Bungoma'),
        ('trans_nzoia', 'Trans Nzoia'),
        ('uasin_gishu', 'Uasin Gishu'),
        ('elgeyo_marakwet', 'Elgeyo Marakwet'),
        ('nandi', 'Nandi'),
        ('baringo', 'Baringo'),
        ('kericho', 'Kericho'),
        ('bomet', 'Bomet'),
        ('nyamira', 'Nyamira'),
        ('kisii', 'Kisii'),
        ('migori', 'Migori'),
        ('homa_bay', 'Homa Bay'),
        ('turkana', 'Turkana'),
        ('west_pokot', 'West Pokot'),
        ('samburu', 'Samburu'),
        ('marsabit', 'Marsabit'),
        ('isiolo', 'Isiolo'),
        ('mombasa', 'Mombasa'),
        ('kwale', 'Kwale'),
        ('kilifi', 'Kilifi'),
        ('tana_river', 'Tana River'),
        ('lamu', 'Lamu'),
        ('taita_taveta', 'Taita Taveta'),
        ('garissa', 'Garissa'),
        ('wajir', 'Wajir'),
        ('mandera', 'Mandera')
    ], validators=[Optional()])
    subcounty = StringField('Sub-County', validators=[Optional(), Length(max=100)])
    ward = StringField('Ward', validators=[Optional(), Length(max=100)])
    facility_name = StringField('Health Facility', validators=[Optional(), Length(max=200)])
    license_number = StringField('License Number', validators=[Optional(), Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])

class PatientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    national_id = StringField('National ID', validators=[Optional(), Length(max=20)])
    nhif_number = StringField('NHIF Number', validators=[Optional(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], widget=DateInput())
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    phone_number = TelField('Phone Number', validators=[Optional(), Length(max=20)])
    email = EmailField('Email', validators=[Optional(), Email()])
    county = SelectField('County', choices=[
        ('', 'Select County'),
        ('nairobi', 'Nairobi'),
        ('kiambu', 'Kiambu'),
        ('machakos', 'Machakos'),
        ('kajiado', 'Kajiado'),
        ('murang\'a', 'Murang\'a'),
        ('nyeri', 'Nyeri'),
        ('kirinyaga', 'Kirinyaga'),
        ('nyandarua', 'Nyandarua'),
        ('nakuru', 'Nakuru'),
        ('laikipia', 'Laikipia'),
        ('meru', 'Meru'),
        ('tharaka_nithi', 'Tharaka Nithi'),
        ('embu', 'Embu'),
        ('kitui', 'Kitui'),
        ('makueni', 'Makueni'),
        ('kisumu', 'Kisumu'),
        ('siaya', 'Siaya'),
        ('busia', 'Busia'),
        ('kakamega', 'Kakamega'),
        ('vihiga', 'Vihiga'),
        ('bungoma', 'Bungoma'),
        ('trans_nzoia', 'Trans Nzoia'),
        ('uasin_gishu', 'Uasin Gishu'),
        ('elgeyo_marakwet', 'Elgeyo Marakwet'),
        ('nandi', 'Nandi'),
        ('baringo', 'Baringo'),
        ('kericho', 'Kericho'),
        ('bomet', 'Bomet'),
        ('nyamira', 'Nyamira'),
        ('kisii', 'Kisii'),
        ('migori', 'Migori'),
        ('homa_bay', 'Homa Bay'),
        ('turkana', 'Turkana'),
        ('west_pokot', 'West Pokot'),
        ('samburu', 'Samburu'),
        ('marsabit', 'Marsabit'),
        ('isiolo', 'Isiolo'),
        ('mombasa', 'Mombasa'),
        ('kwale', 'Kwale'),
        ('kilifi', 'Kilifi'),
        ('tana_river', 'Tana River'),
        ('lamu', 'Lamu'),
        ('taita_taveta', 'Taita Taveta'),
        ('garissa', 'Garissa'),
        ('wajir', 'Wajir'),
        ('mandera', 'Mandera')
    ], validators=[Optional()])
    subcounty = StringField('Sub-County', validators=[Optional(), Length(max=100)])
    ward = StringField('Ward', validators=[Optional(), Length(max=100)])
    village = StringField('Village', validators=[Optional(), Length(max=100)])
    address_line = TextAreaField('Address', validators=[Optional()])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Unknown'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[Optional()])
    allergies = TextAreaField('Known Allergies', validators=[Optional()])
    chronic_conditions = TextAreaField('Chronic Conditions', validators=[Optional()])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=200)])
    emergency_contact_phone = TelField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])

class HealthRecordForm(FlaskForm):
    encounter_type = SelectField('Encounter Type', choices=[
        ('consultation', 'Consultation'),
        ('screening', 'Health Screening'),
        ('vaccination', 'Vaccination'),
        ('follow_up', 'Follow-up Visit'),
        ('emergency', 'Emergency Care'),
        ('antenatal', 'Antenatal Care'),
        ('postnatal', 'Postnatal Care'),
        ('family_planning', 'Family Planning'),
        ('chronic_care', 'Chronic Disease Management')
    ], validators=[DataRequired()])
    
    # Vital signs
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0, max=500)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=0, max=300)])
    temperature = FloatField('Temperature (°C)', validators=[Optional(), NumberRange(min=30, max=50)])
    blood_pressure_systolic = IntegerField('Systolic BP', validators=[Optional(), NumberRange(min=50, max=300)])
    blood_pressure_diastolic = IntegerField('Diastolic BP', validators=[Optional(), NumberRange(min=30, max=200)])
    pulse_rate = IntegerField('Pulse Rate (bpm)', validators=[Optional(), NumberRange(min=30, max=200)])
    
    # Clinical information
    chief_complaint = TextAreaField('Chief Complaint', validators=[Optional()])
    diagnosis = TextAreaField('Diagnosis', validators=[Optional()])
    treatment_plan = TextAreaField('Treatment Plan', validators=[Optional()])
    medications_prescribed = TextAreaField('Medications Prescribed', validators=[Optional()])
    follow_up_date = DateField('Follow-up Date', validators=[Optional()], widget=DateInput())
    facility_name = StringField('Facility Name', validators=[Optional(), Length(max=200)])

class OutreachEventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    event_type = SelectField('Event Type', choices=[
        ('vaccination', 'Vaccination Campaign'),
        ('screening', 'Health Screening'),
        ('education', 'Health Education'),
        ('nutrition', 'Nutrition Program'),
        ('maternal_health', 'Maternal Health'),
        ('child_health', 'Child Health'),
        ('family_planning', 'Family Planning'),
        ('mental_health', 'Mental Health'),
        ('chronic_disease', 'Chronic Disease Management'),
        ('emergency_prep', 'Emergency Preparedness')
    ], validators=[DataRequired()])
    
    start_date = DateField('Start Date', validators=[DataRequired()], widget=DateInput())
    end_date = DateField('End Date', validators=[DataRequired()], widget=DateInput())
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    
    target_county = SelectField('Target County', choices=[
        ('', 'All Counties'),
        ('nairobi', 'Nairobi'),
        ('kiambu', 'Kiambu'),
        ('machakos', 'Machakos'),
        ('kajiado', 'Kajiado'),
        ('murang\'a', 'Murang\'a'),
        ('nyeri', 'Nyeri'),
        ('kirinyaga', 'Kirinyaga'),
        ('nyandarua', 'Nyandarua'),
        ('nakuru', 'Nakuru'),
        ('laikipia', 'Laikipia'),
        ('meru', 'Meru'),
        ('tharaka_nithi', 'Tharaka Nithi'),
        ('embu', 'Embu'),
        ('kitui', 'Kitui'),
        ('makueni', 'Makueni'),
        ('kisumu', 'Kisumu'),
        ('siaya', 'Siaya'),
        ('busia', 'Busia'),
        ('kakamega', 'Kakamega'),
        ('vihiga', 'Vihiga'),
        ('bungoma', 'Bungoma'),
        ('trans_nzoia', 'Trans Nzoia'),
        ('uasin_gishu', 'Uasin Gishu'),
        ('elgeyo_marakwet', 'Elgeyo Marakwet'),
        ('nandi', 'Nandi'),
        ('baringo', 'Baringo'),
        ('kericho', 'Kericho'),
        ('bomet', 'Bomet'),
        ('nyamira', 'Nyamira'),
        ('kisii', 'Kisii'),
        ('migori', 'Migori'),
        ('homa_bay', 'Homa Bay'),
        ('turkana', 'Turkana'),
        ('west_pokot', 'West Pokot'),
        ('samburu', 'Samburu'),
        ('marsabit', 'Marsabit'),
        ('isiolo', 'Isiolo'),
        ('mombasa', 'Mombasa'),
        ('kwale', 'Kwale'),
        ('kilifi', 'Kilifi'),
        ('tana_river', 'Tana River'),
        ('lamu', 'Lamu'),
        ('taita_taveta', 'Taita Taveta'),
        ('garissa', 'Garissa'),
        ('wajir', 'Wajir'),
        ('mandera', 'Mandera')
    ], validators=[Optional()])
    target_subcounty = StringField('Target Sub-County', validators=[Optional(), Length(max=100)])
    target_ward = StringField('Target Ward', validators=[Optional(), Length(max=100)])
    
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1)])
    target_age_min = IntegerField('Minimum Age', validators=[Optional(), NumberRange(min=0, max=120)])
    target_age_max = IntegerField('Maximum Age', validators=[Optional(), NumberRange(min=0, max=120)])
    target_gender = SelectField('Target Gender', choices=[
        ('all', 'All'),
        ('male', 'Male'),
        ('female', 'Female')
    ], validators=[Optional()])

class PaymentForm(FlaskForm):
    amount = FloatField('Amount (KES)', validators=[DataRequired(), NumberRange(min=1)])
    payment_type = SelectField('Payment Type', choices=[
        ('consultation_fee', 'Consultation Fee'),
        ('treatment_fee', 'Treatment Fee'),
        ('medication_fee', 'Medication Fee'),
        ('screening_fee', 'Screening Fee'),
        ('chw_allowance', 'CHW Allowance'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    phone_number = TelField('M-Pesa Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
