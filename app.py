# app.py - Main Flask Application

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import google.generativeai as genai
import os
from dotenv import load_dotenv

app = Flask(__name__)

app.secret_key = 'hospital_management_secret_key'

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAhP_YoIRSRkclMeRJaOQk_5Z4Bh9JAjXo"
genai.configure(api_key=GEMINI_API_KEY)

# Create a Gemini model
def get_gemini_model():
    return genai.GenerativeModel('gemini-2.0-flash')

# Function to generate medical chatbot responses
def generate_medical_response(prompt, patient_info=None):
    try:
        model = get_gemini_model()
        
        # Add context if patient info is available
        if patient_info:
            system_prompt = f"""
            You are a helpful medical assistant for a hospital management system.
            You are helping a patient with the following information:
            - Name: {patient_info['name']}
            - Age: {patient_info['age']}
            - Gender: {patient_info['gender']}
            - Medical History: {patient_info['medical_history']}
            - Blood Group: {patient_info['blood_group']}
            Format the whole thing, Make it fully structured please. I don't want unnecessary things only what I ask.

            Provide helpful medical information based on the patient's question.
            Always recommend consulting with a doctor for specific medical advice.
            Do not provide definitive diagnoses or prescribe medications.
            """
            
            response = model.generate_content([system_prompt, prompt])
        else:
            # General medical assistant context
            system_prompt = """
            You are a helpful medical assistant for a hospital management system.
            Provide general medical information based on the user's question.
            Always recommend consulting with a doctor for specific medical advice.
            Do not provide definitive diagnoses or prescribe medications.
            Keep your responses concise and informative.
            """
            
            response = model.generate_content([system_prompt, prompt])
        
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"


# Database Setup
DB_PATH = 'hospital_management.db'

def init_db():
    # Check if database file exists
    db_exists = os.path.exists(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if database doesn't exist
    if not db_exists:
        # Admin table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Admin (
            AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            FullName TEXT NOT NULL,
            LastLogin DATETIME,
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Doctor table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Doctor (
            DoctorID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Specialisation TEXT NOT NULL,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            ContactNumber TEXT,
            Email TEXT,
            AddedByAdmin INTEGER,
            JoinDate DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (AddedByAdmin) REFERENCES Admin(AdminID)
        )
        ''')
        
        # Patient table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Patient (
            PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Age INTEGER CHECK (Age > 0),
            Gender TEXT CHECK (Gender IN ('Male', 'Female', 'Other')),
            Password TEXT NOT NULL,
            ContactNumber TEXT,
            Email TEXT,
            Address TEXT,
            MedicalHistory TEXT,
            BloodGroup TEXT,
            AssignedDoctorID INTEGER,
            RegistrationDate DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (AssignedDoctorID) REFERENCES Doctor(DoctorID)
        )
        ''')
        
        # Diagnosis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Diagnosis (
            DiagnosisID INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientID INTEGER NOT NULL,
            Symptoms TEXT NOT NULL,
            Diagnosis TEXT NOT NULL,
            Notes TEXT,
            Date DATE DEFAULT CURRENT_DATE,
            DiagnosedBy INTEGER NOT NULL,
            FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
            FOREIGN KEY (DiagnosedBy) REFERENCES Doctor(DoctorID)
        )
        ''')
        
        # MedicalRecord table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MedicalRecord (
            RecordID INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientID INTEGER NOT NULL,
            Diagnosis TEXT NOT NULL,
            Treatment TEXT NOT NULL,
            PrescribedBy INTEGER NOT NULL,
            RecordDate DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
            FOREIGN KEY (PrescribedBy) REFERENCES Doctor(DoctorID)
        )
        ''')
        
        # Appointment table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Appointment (
            AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientID INTEGER NOT NULL,
            DoctorID INTEGER NOT NULL,
            Date DATE NOT NULL,
            Time TEXT NOT NULL,
            Status TEXT DEFAULT 'Scheduled' CHECK (Status IN ('Scheduled', 'Completed', 'Cancelled')),
            Purpose TEXT,
            FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
            FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
        )
        ''')
        
        # DoctorPatient junction table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS DoctorPatient (
            DoctorPatientID INTEGER PRIMARY KEY AUTOINCREMENT,
            DoctorID INTEGER NOT NULL,
            PatientID INTEGER NOT NULL,
            RelationshipStartDate DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID),
            FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
            UNIQUE(DoctorID, PatientID)
        )
        ''')
        
        # Insert sample data
        # Insert Admin records
        cursor.execute("INSERT INTO Admin (Username, Password, FullName) VALUES (?, ?, ?)", 
                       ('admin_aayush', generate_password_hash('admin@123'), 'Aayush Mishra'))
        cursor.execute("INSERT INTO Admin (Username, Password, FullName) VALUES (?, ?, ?)", 
                       ('admin_ushnish', generate_password_hash('admin#456'), 'Ushnish Ghosal'))
        cursor.execute("INSERT INTO Admin (Username, Password, FullName) VALUES (?, ?, ?)", 
                       ('admin_utsav', generate_password_hash('admin!789'), 'Utsav Opal'))
        
        # Insert Doctors
        cursor.execute('''
        INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Dr. Rajesh Khanna', 'Cardiology', 'dr_rajesh', generate_password_hash('doc@123'), 
              '+919876543210', 'dr.rajesh@example.com', 1))
        
        cursor.execute('''
        INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Dr. Priya Sharma', 'Pediatrics', 'dr_priya', generate_password_hash('pedia#456'), 
              '+919765432109', 'dr.priya@example.com', 1))
        
        cursor.execute('''
        INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Dr. Amit Patel', 'Orthopedics', 'dr_amit', generate_password_hash('ortho789'), 
              '+919654321098', 'dr.amit@example.com', 2))
        
        cursor.execute('''
        INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Dr. Ananya Reddy', 'Neurology', 'dr_ananya', generate_password_hash('neuro101'), 
              '+919543210987', 'dr.ananya@example.com', 2))
        
        # Insert Patients
        cursor.execute('''
        INSERT INTO Patient (Name, Age, Gender, Password, ContactNumber, Email, Address, MedicalHistory, BloodGroup, AssignedDoctorID) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Rahul Verma', 45, 'Male', generate_password_hash('patient@123'), '+919812345678', 
              'rahul.v@example.com', '12, Green Park, New Delhi', 'Hypertension since 2018', 'B+', 1))
        
        cursor.execute('''
        INSERT INTO Patient (Name, Age, Gender, Password, ContactNumber, Email, Address, MedicalHistory, BloodGroup, AssignedDoctorID) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Neha Gupta', 32, 'Female', generate_password_hash('neha#456'), '+919712345678', 
              'neha.g@example.com', '34, Andheri East, Mumbai', 'Asthma, Allergic rhinitis', 'A+', 2))
        
        # Add more sample data as needed...
        
        conn.commit()
    
    conn.close()

# Initialize the database when app starts
init_db()

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        conn = get_db_connection()
        
        if user_type == 'admin':
            user = conn.execute('SELECT * FROM Admin WHERE Username = ?', (username,)).fetchone()
        elif user_type == 'doctor':
            user = conn.execute('SELECT * FROM Doctor WHERE Username = ?', (username,)).fetchone()
        else:  # patient
            user = conn.execute('SELECT * FROM Patient WHERE Email = ?', (username,)).fetchone()
        
        conn.close()
        
        if user and check_password_hash(user['Password'], password):
            # Login successful
            session['user_id'] = user['AdminID' if user_type == 'admin' else 'DoctorID' if user_type == 'doctor' else 'PatientID']
            session['user_type'] = user_type
            session['username'] = username
            
            # Update last login for admin
            if user_type == 'admin':
                conn = get_db_connection()
                conn.execute('UPDATE Admin SET LastLogin = ? WHERE AdminID = ?', 
                            (datetime.now(), user['AdminID']))
                conn.commit()
                conn.close()
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    # For GET method, show the user type selection page
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"response": "Please log in to use the medical chatbot."})
    
    data = request.get_json()
    query = data.get('query', '')
    
    # If patient is logged in, provide personalized responses
    if session.get('user_type') == 'patient':
        patient_id = session.get('user_id')
        
        # Get patient information
        conn = get_db_connection()
        patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (patient_id,)).fetchone()
        conn.close()
        
        if patient:
            patient_info = {
                'name': patient['Name'],
                'age': patient['Age'],
                'gender': patient['Gender'],
                'medical_history': patient['MedicalHistory'],
                'blood_group': patient['BloodGroup']
            }
            response = generate_medical_response(query, patient_info)
        else:
            response = generate_medical_response(query)
    else:
        # Generic response for doctors and admins
        response = generate_medical_response(query)
    
    return jsonify({"response": response})

@app.route('/admin/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def admin_edit_appointment(appointment_id):
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get the appointment details
    appointment = conn.execute('''
    SELECT a.*, p.Name as PatientName, d.Name as DoctorName 
    FROM Appointment a 
    JOIN Patient p ON a.PatientID = p.PatientID 
    JOIN Doctor d ON a.DoctorID = d.DoctorID 
    WHERE a.AppointmentID = ?
    ''', (appointment_id,)).fetchone()
    
    if not appointment:
        conn.close()
        flash('Appointment not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all doctors and patients for the dropdown menus
    doctors = conn.execute('SELECT * FROM Doctor').fetchall()
    patients = conn.execute('SELECT * FROM Patient').fetchall()
    
    if request.method == 'POST':
        # Get form data
        doctor_id = request.form.get('doctor_id')
        patient_id = request.form.get('patient_id')
        date = request.form.get('date')
        time = request.form.get('time')
        status = request.form.get('status')
        purpose = request.form.get('purpose')
        
        if not all([doctor_id, patient_id, date, time, status]):
            flash('All required fields must be filled', 'error')
        else:
            try:
                # Update the appointment
                conn.execute('''
                UPDATE Appointment 
                SET DoctorID = ?, PatientID = ?, Date = ?, Time = ?, Status = ?, Purpose = ? 
                WHERE AppointmentID = ?
                ''', (doctor_id, patient_id, date, time, status, purpose, appointment_id))
                
                conn.commit()
                flash('Appointment updated successfully', 'success')
                return redirect(url_for('dashboard'))
            
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('admin/edit_appointment.html', 
                          appointment=appointment,
                          doctors=doctors,
                          patients=patients)

@app.route('/patient/edit_profile', methods=['GET', 'POST'])
def patient_edit_profile():
    if 'user_id' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (patient_id,)).fetchone()
    
    if not patient:
        conn.close()
        flash('Patient not found', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        contact_number = request.form.get('contact_number')
        email = request.form.get('email')
        address = request.form.get('address')
        medical_history = request.form.get('medical_history')
        
        try:
            # Update patient information
            conn.execute('''
            UPDATE Patient 
            SET ContactNumber = ?, Email = ?, Address = ?, MedicalHistory = ? 
            WHERE PatientID = ?
            ''', (contact_number, email, address, medical_history, patient_id))
            
            conn.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('patient_profile'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('patient/edit_profile.html', patient=patient)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = session['user_type']
    user_id = session['user_id']
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))
        
        conn = get_db_connection()
        
        # Get user based on type
        if user_type == 'admin':
            user = conn.execute('SELECT * FROM Admin WHERE AdminID = ?', (user_id,)).fetchone()
            table = 'Admin'
            id_column = 'AdminID'
        elif user_type == 'doctor':
            user = conn.execute('SELECT * FROM Doctor WHERE DoctorID = ?', (user_id,)).fetchone()
            table = 'Doctor'
            id_column = 'DoctorID'
        else:  # patient
            user = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (user_id,)).fetchone()
            table = 'Patient'
            id_column = 'PatientID'
        
        # Verify current password
        if not check_password_hash(user['Password'], current_password):
            conn.close()
            flash('Current password is incorrect', 'error')
            return redirect(url_for('change_password'))
        
        # Update password
        hashed_password = generate_password_hash(new_password)
        conn.execute(f'UPDATE {table} SET Password = ? WHERE {id_column} = ?', 
                    (hashed_password, user_id))
        
        conn.commit()
        conn.close()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

@app.route('/doctor/edit_profile', methods=['GET', 'POST'])
def doctor_edit_profile():
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    
    conn = get_db_connection()
    doctor = conn.execute('SELECT * FROM Doctor WHERE DoctorID = ?', (doctor_id,)).fetchone()
    
    if not doctor:
        conn.close()
        flash('Doctor not found', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        contact_number = request.form.get('contact_number')
        email = request.form.get('email')
        specialisation = request.form.get('specialisation')
        
        try:
            # Update doctor information
            conn.execute('''
            UPDATE Doctor 
            SET ContactNumber = ?, Email = ?, Specialisation = ? 
            WHERE DoctorID = ?
            ''', (contact_number, email, specialisation, doctor_id))
            
            conn.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('doctor/edit_profile.html', doctor=doctor)

@app.route('/doctor/add_appointment', methods=['GET', 'POST'])
def doctor_add_appointment():
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    
    # Get all patients assigned to this doctor
    patients = conn.execute('''
    SELECT p.* FROM Patient p 
    JOIN DoctorPatient dp ON p.PatientID = dp.PatientID 
    WHERE dp.DoctorID = ?
    ''', (doctor_id,)).fetchall()
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        date = request.form.get('date')
        time = request.form.get('time')
        purpose = request.form.get('purpose')
        
        if not all([patient_id, date, time]):
            flash('Patient, date and time are required', 'error')
        else:
            try:
                conn.execute('''
                INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose) 
                VALUES (?, ?, ?, ?, ?)
                ''', (patient_id, doctor_id, date, time, purpose))
                
                conn.commit()
                flash('Appointment added successfully', 'success')
                return redirect(url_for('doctor_appointments'))
            
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('doctor/add_appointment.html', 
                           patients=patients, 
                           current_date=current_date)

@app.route('/doctor/calendar')
def doctor_calendar():
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    
    # Get doctor info
    doctor = conn.execute('SELECT * FROM Doctor WHERE DoctorID = ?', (doctor_id,)).fetchone()
    
    # Get all appointments
    appointments = conn.execute('''
    SELECT a.*, p.Name as PatientName 
    FROM Appointment a 
    JOIN Patient p ON a.PatientID = p.PatientID 
    WHERE a.DoctorID = ? 
    ORDER BY a.Date, a.Time
    ''', (doctor_id,)).fetchall()
    
    # Count statistics
    today_appointments = 0
    week_appointments = 0
    month_appointments = 0
    
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_end = week_start + timedelta(days=6)
    week_start_str = week_start.strftime('%Y-%m-%d')
    week_end_str = week_end.strftime('%Y-%m-%d')
    
    month_start = datetime.now().replace(day=1)
    next_month = month_start.replace(day=28) + timedelta(days=4)
    month_end = next_month - timedelta(days=next_month.day)
    month_start_str = month_start.strftime('%Y-%m-%d')
    month_end_str = month_end.strftime('%Y-%m-%d')
    
    # Process appointments
    calendar_events = []
    
    for app in appointments:
        # Count statistics
        if app['Status'] == 'Scheduled':
            if app['Date'] == current_date:
                today_appointments += 1
            
            if app['Date'] >= week_start_str and app['Date'] <= week_end_str:
                week_appointments += 1
            
            if app['Date'] >= month_start_str and app['Date'] <= month_end_str:
                month_appointments += 1
        
        # Create calendar events
        # Ensure time format is correct (HH:MM:SS)
        time_parts = app['Time'].split(':')
        start_time = app['Time']
        if len(time_parts) == 2:
            start_time = f"{time_parts[0]}:{time_parts[1]}:00"
        
        # Calculate end time (30 min after start)
        hour = int(time_parts[0])
        minute = int(time_parts[1]) + 30
        
        if minute >= 60:
            hour += 1
            minute -= 60
        
        end_time = f"{hour:02d}:{minute:02d}:00"
        
        # Set start and end datetime strings for the event
        start_datetime = f"{app['Date']}T{start_time}"
        end_datetime = f"{app['Date']}T{end_time}"
        
        # Set color based on status
        color = "#ffc107"  # Yellow for Scheduled
        if app['Status'] == 'Completed':
            color = "#28a745"  # Green for Completed
        elif app['Status'] == 'Cancelled':
            color = "#dc3545"  # Red for Cancelled
        
        # Create event object
        event = {
            'id': app['AppointmentID'],
            'title': f"{app['PatientName']} - {app['Purpose'] if app['Purpose'] else 'Checkup'}",
            'start': start_datetime,
            'end': end_datetime,
            'color': color,
            'extendedProps': {
                'patientId': app['PatientID'],
                'status': app['Status'],
                'purpose': app['Purpose']
            }
        }
        
        calendar_events.append(event)
    
    conn.close()
    
    # Convert to JSON for use in JavaScript
    import json
    
    # Debug the output
    print("Calendar Events JSON:")
    print(json.dumps(calendar_events, indent=2))
    
    return render_template('doctor/calendar.html', 
                          doctor=doctor, 
                          today_appointments=today_appointments,
                          week_appointments=week_appointments,
                          month_appointments=month_appointments,
                          calendar_events_json=json.dumps(calendar_events))

@app.route('/doctor/edit_diagnosis/<int:diagnosis_id>', methods=['GET', 'POST'])
def doctor_edit_diagnosis(diagnosis_id):
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    
    # Get the diagnosis and verify it belongs to this doctor
    diagnosis = conn.execute('''
    SELECT d.*, p.Name as PatientName
    FROM Diagnosis d 
    JOIN Patient p ON d.PatientID = p.PatientID
    WHERE d.DiagnosisID = ? AND d.DiagnosedBy = ?
    ''', (diagnosis_id, doctor_id)).fetchone()
    
    if not diagnosis:
        conn.close()
        flash('Diagnosis not found or you do not have permission to edit it', 'error')
        return redirect(url_for('doctor_patients'))
    
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        diagnosis_text = request.form.get('diagnosis')
        notes = request.form.get('notes')
        date = request.form.get('date')
        
        if not all([symptoms, diagnosis_text]):
            flash('Symptoms and diagnosis are required', 'error')
        else:
            try:
                conn.execute('''
                UPDATE Diagnosis 
                SET Symptoms = ?, Diagnosis = ?, Notes = ?, Date = ? 
                WHERE DiagnosisID = ? AND DiagnosedBy = ?
                ''', (symptoms, diagnosis_text, notes, date, diagnosis_id, doctor_id))
                
                conn.commit()
                flash('Diagnosis updated successfully', 'success')
                return redirect(url_for('doctor_view_patient', patient_id=diagnosis['PatientID']))
            
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('doctor/edit_diagnosis.html', diagnosis=diagnosis, current_date=current_date)

@app.route('/login/patient', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Patient WHERE Email = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['Password'], password):
            # Login successful
            session['user_id'] = user['PatientID']
            session['user_type'] = 'patient'
            session['username'] = username
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('patient_login.html')

@app.route('/login/doctor', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Doctor WHERE Username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['Password'], password):
            # Login successful
            session['user_id'] = user['DoctorID']
            session['user_type'] = 'doctor'
            session['username'] = username
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('doctor_login.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Admin WHERE Username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['Password'], password):
            # Login successful
            session['user_id'] = user['AdminID']
            session['user_type'] = 'admin'
            session['username'] = username
            
            # Update last login for admin
            conn.execute('UPDATE Admin SET LastLogin = ? WHERE AdminID = ?', 
                        (datetime.now(), user['AdminID']))
            conn.commit()
            conn.close()
            
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add this line to get current date
    
    conn = get_db_connection()
    
    if user_type == 'admin':
        # Admin dashboard data
        doctors = conn.execute('SELECT * FROM Doctor').fetchall()
        patients = conn.execute('SELECT * FROM Patient').fetchall()
        appointments = conn.execute('''
        SELECT a.*, p.Name as PatientName, d.Name as DoctorName 
        FROM Appointment a 
        JOIN Patient p ON a.PatientID = p.PatientID 
        JOIN Doctor d ON a.DoctorID = d.DoctorID 
        ORDER BY a.Date, a.Time
        ''').fetchall()
        
        return render_template('admin_dashboard.html', 
                              doctors=doctors, 
                              patients=patients, 
                              appointments=appointments,
                              current_date=current_date)  # Add current_date here
    
    elif user_type == 'doctor':
        # Doctor dashboard data
        doctor = conn.execute('SELECT * FROM Doctor WHERE DoctorID = ?', (user_id,)).fetchone()
        doctor_patients = conn.execute('''
        SELECT p.* FROM Patient p 
        JOIN DoctorPatient dp ON p.PatientID = dp.PatientID 
        WHERE dp.DoctorID = ?
        ''', (user_id,)).fetchall()
        
        upcoming_appointments = conn.execute('''
        SELECT a.*, p.Name as PatientName 
        FROM Appointment a 
        JOIN Patient p ON a.PatientID = p.PatientID 
        WHERE a.DoctorID = ? AND a.Status = 'Scheduled' AND a.Date >= date('now') 
        ORDER BY a.Date, a.Time
        ''', (user_id,)).fetchall()
        
        return render_template('doctor_dashboard.html', 
                              doctor=doctor, 
                              patients=doctor_patients, 
                              appointments=upcoming_appointments,
                              current_date=current_date)  # Add current_date here
    
    elif user_type == 'patient':
        # Patient dashboard data
        patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (user_id,)).fetchone()
        
        doctor = None
        if patient['AssignedDoctorID']:
            doctor = conn.execute('SELECT * FROM Doctor WHERE DoctorID = ?', 
                                 (patient['AssignedDoctorID'],)).fetchone()
        
        appointments = conn.execute('''
        SELECT a.*, d.Name as DoctorName 
        FROM Appointment a 
        JOIN Doctor d ON a.DoctorID = d.DoctorID 
        WHERE a.PatientID = ? 
        ORDER BY a.Date DESC, a.Time
        ''', (user_id,)).fetchall()
        
        medical_records = conn.execute('''
        SELECT mr.*, d.Name as DoctorName 
        FROM MedicalRecord mr 
        JOIN Doctor d ON mr.PrescribedBy = d.DoctorID 
        WHERE mr.PatientID = ? 
        ORDER BY mr.RecordDate DESC
        ''', (user_id,)).fetchall()
        
        diagnoses = conn.execute('''
        SELECT diag.*, d.Name as DoctorName 
        FROM Diagnosis diag 
        JOIN Doctor d ON diag.DiagnosedBy = d.DoctorID 
        WHERE diag.PatientID = ? 
        ORDER BY diag.Date DESC
        ''', (user_id,)).fetchall()
        
        return render_template('patient_dashboard.html', 
                              patient=patient, 
                              doctor=doctor,
                              appointments=appointments,
                              medical_records=medical_records,
                              diagnoses=diagnoses,
                              current_date=current_date)  # Add current_date here
    
    conn.close()
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/doctors')
def admin_doctors():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM Doctor').fetchall()
    conn.close()
    
    return render_template('admin/doctors.html', doctors=doctors)

@app.route('/admin/add_doctor', methods=['GET', 'POST'])
def admin_add_doctor():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        specialisation = request.form.get('specialisation')
        username = request.form.get('username')
        password = request.form.get('password')
        contact = request.form.get('contact')
        email = request.form.get('email')
        
        if not all([name, specialisation, username, password]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('admin_add_doctor'))
        
        try:
            conn = get_db_connection()
            # Check if username exists
            existing = conn.execute('SELECT * FROM Doctor WHERE Username = ?', (username,)).fetchone()
            
            if existing:
                conn.close()
                flash('Username already exists', 'error')
                return redirect(url_for('admin_add_doctor'))
            
            # Add new doctor
            hashed_password = generate_password_hash(password)
            conn.execute('''
            INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, specialisation, username, hashed_password, contact, email, session['user_id']))
            
            conn.commit()
            conn.close()
            
            flash('Doctor added successfully', 'success')
            return redirect(url_for('admin_doctors'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin_add_doctor'))
    
    return render_template('admin/add_doctor.html')

@app.route('/admin/patients')
def admin_patients():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    patients = conn.execute('''
    SELECT p.*, d.Name as DoctorName 
    FROM Patient p 
    LEFT JOIN Doctor d ON p.AssignedDoctorID = d.DoctorID
    ''').fetchall()
    conn.close()
    
    return render_template('admin/patients.html', patients=patients)

@app.route('/admin/add_patient', methods=['GET', 'POST'])
def admin_add_patient():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM Doctor').fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        password = request.form.get('password')
        contact = request.form.get('contact')
        email = request.form.get('email')
        address = request.form.get('address')
        medical_history = request.form.get('medical_history')
        blood_group = request.form.get('blood_group')
        doctor_id = request.form.get('doctor_id')
        
        if not doctor_id:
            doctor_id = None
        
        if not all([name, age, gender, password]):
            flash('All required fields must be filled', 'error')
            return redirect(url_for('admin_add_patient'))
        
        try:
            # Add new patient
            hashed_password = generate_password_hash(password)
            
            cursor = conn.execute('''
            INSERT INTO Patient (Name, Age, Gender, Password, ContactNumber, Email, Address, MedicalHistory, BloodGroup, AssignedDoctorID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, age, gender, hashed_password, contact, email, address, medical_history, blood_group, doctor_id))
            
            # If doctor is assigned, add entry to DoctorPatient
            if doctor_id:
                patient_id = cursor.lastrowid
                conn.execute('''
                INSERT INTO DoctorPatient (DoctorID, PatientID) 
                VALUES (?, ?)
                ''', (doctor_id, patient_id))
            
            conn.commit()
            
            flash('Patient added successfully', 'success')
            return redirect(url_for('admin_patients'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    return render_template('admin/add_patient.html', doctors=doctors)

# Doctor routes
@app.route('/doctor/patients')
def doctor_patients():
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    
    conn = get_db_connection()
    patients = conn.execute('''
    SELECT p.* FROM Patient p 
    JOIN DoctorPatient dp ON p.PatientID = dp.PatientID 
    WHERE dp.DoctorID = ?
    ''', (doctor_id,)).fetchall()
    conn.close()
    
    return render_template('doctor/patients.html', patients=patients)

@app.route('/doctor/patient/<int:patient_id>')
def doctor_view_patient(patient_id):
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    
    # Check if this patient is assigned to the doctor
    relationship = conn.execute('''
    SELECT * FROM DoctorPatient 
    WHERE DoctorID = ? AND PatientID = ?
    ''', (doctor_id, patient_id)).fetchone()
    
    if not relationship:
        conn.close()
        flash('Patient not found or not assigned to you', 'error')
        return redirect(url_for('doctor_patients'))
    
    patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (patient_id,)).fetchone()
    
    diagnoses = conn.execute('''
    SELECT * FROM Diagnosis 
    WHERE PatientID = ? AND DiagnosedBy = ? 
    ORDER BY Date DESC
    ''', (patient_id, doctor_id)).fetchall()
    
    medical_records = conn.execute('''
    SELECT * FROM MedicalRecord 
    WHERE PatientID = ? AND PrescribedBy = ? 
    ORDER BY RecordDate DESC
    ''', (patient_id, doctor_id)).fetchall()
    
    appointments = conn.execute('''
    SELECT * FROM Appointment 
    WHERE PatientID = ? AND DoctorID = ? 
    ORDER BY Date DESC, Time
    ''', (patient_id, doctor_id)).fetchall()
    
    conn.close()
    
    return render_template('doctor/patient_details.html', 
                          patient=patient, 
                          diagnoses=diagnoses,
                          medical_records=medical_records,
                          appointments=appointments,
                          current_date=current_date)  # Add current_date here


@app.route('/doctor/add_diagnosis/<int:patient_id>', methods=['GET', 'POST'])
def doctor_add_diagnosis(patient_id):
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (patient_id,)).fetchone()
    
    if not patient:
        conn.close()
        flash('Patient not found', 'error')
        return redirect(url_for('doctor_patients'))
    
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        diagnosis = request.form.get('diagnosis')
        notes = request.form.get('notes')
        date = request.form.get('date')
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if not all([symptoms, diagnosis]):
            flash('Symptoms and diagnosis are required', 'error')
        else:
            try:
                conn.execute('''
                INSERT INTO Diagnosis (PatientID, Symptoms, Diagnosis, Notes, Date, DiagnosedBy) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (patient_id, symptoms, diagnosis, notes, date, doctor_id))
                
                conn.commit()
                flash('Diagnosis added successfully', 'success')
                return redirect(url_for('doctor_view_patient', patient_id=patient_id))
            
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('doctor/add_diagnosis.html', patient=patient, current_date=current_date)


@app.route('/doctor/add_medical_record/<int:patient_id>', methods=['GET', 'POST'])
def doctor_add_medical_record(patient_id):
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (patient_id,)).fetchone()
    
    if not patient:
        conn.close()
        flash('Patient not found', 'error')
        return redirect(url_for('doctor_patients'))
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        date = request.form.get('date')
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if not all([diagnosis, treatment]):
            flash('Diagnosis and treatment are required', 'error')
        else:
            try:
                conn.execute('''
                INSERT INTO MedicalRecord (PatientID, Diagnosis, Treatment, RecordDate, PrescribedBy) 
                VALUES (?, ?, ?, ?, ?)
                ''', (patient_id, diagnosis, treatment, date, doctor_id))
                
                conn.commit()
                flash('Medical record added successfully', 'success')
                return redirect(url_for('doctor_view_patient', patient_id=patient_id))
            
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('doctor/add_medical_record.html', patient=patient, current_date=current_date)
@app.route('/doctor/appointments')
def doctor_appointments():
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    
    upcoming = conn.execute('''
    SELECT a.*, p.Name as PatientName 
    FROM Appointment a 
    JOIN Patient p ON a.PatientID = p.PatientID 
    WHERE a.DoctorID = ? AND a.Status = 'Scheduled' AND a.Date >= date('now') 
    ORDER BY a.Date, a.Time
    ''', (doctor_id,)).fetchall()
    
    past = conn.execute('''
    SELECT a.*, p.Name as PatientName 
    FROM Appointment a 
    JOIN Patient p ON a.PatientID = p.PatientID 
    WHERE a.DoctorID = ? AND (a.Status != 'Scheduled' OR a.Date < date('now')) 
    ORDER BY a.Date DESC, a.Time
    ''', (doctor_id,)).fetchall()
    
    conn.close()
    
    return render_template('doctor/appointments.html', 
                          upcoming=upcoming, 
                          past=past,
                          current_date=current_date)  # Add current_date here

@app.route('/doctor/update_appointment/<int:appointment_id>', methods=['POST'])
def doctor_update_appointment(appointment_id):
    if 'user_id' not in session or session['user_type'] != 'doctor':
        return redirect(url_for('login'))
    
    doctor_id = session['user_id']
    status = request.form.get('status')
    
    if not status or status not in ['Scheduled', 'Completed', 'Cancelled']:
        flash('Invalid status', 'error')
        return redirect(url_for('doctor_appointments'))
    
    conn = get_db_connection()
    
    # Verify this appointment belongs to the doctor
    appointment = conn.execute('''
    SELECT * FROM Appointment WHERE AppointmentID = ? AND DoctorID = ?
    ''', (appointment_id, doctor_id)).fetchone()
    
    if not appointment:
        conn.close()
        flash('Appointment not found', 'error')
        return redirect(url_for('doctor_appointments'))
    
    # Update status
    conn.execute('''
    UPDATE Appointment SET Status = ? WHERE AppointmentID = ?
    ''', (status, appointment_id))
    
    conn.commit()
    conn.close()
    
    flash('Appointment updated successfully', 'success')
    return redirect(url_for('doctor_appointments'))

# Patient routes
@app.route('/patient/profile')
def patient_profile():
    if 'user_id' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    
    conn = get_db_connection()
    
    patient = conn.execute('SELECT * FROM Patient WHERE PatientID = ?', (patient_id,)).fetchone()
    
    doctor = None
    if patient['AssignedDoctorID']:
        doctor = conn.execute('SELECT * FROM Doctor WHERE DoctorID = ?', 
                             (patient['AssignedDoctorID'],)).fetchone()
    
    conn.close()
    
    return render_template('patient/profile.html', patient=patient, doctor=doctor)

@app.route('/patient/appointments')
def patient_appointments():
    if 'user_id' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    
    upcoming = conn.execute('''
    SELECT a.*, d.Name as DoctorName, d.Specialisation as DoctorSpecialisation
    FROM Appointment a 
    JOIN Doctor d ON a.DoctorID = d.DoctorID 
    WHERE a.PatientID = ? AND a.Status = 'Scheduled' AND a.Date >= date('now') 
    ORDER BY a.Date, a.Time
    ''', (patient_id,)).fetchall()
    
    past = conn.execute('''
    SELECT a.*, d.Name as DoctorName, d.Specialisation as DoctorSpecialisation
    FROM Appointment a 
    JOIN Doctor d ON a.DoctorID = d.DoctorID 
    WHERE a.PatientID = ? AND (a.Status != 'Scheduled' OR a.Date < date('now')) 
    ORDER BY a.Date DESC, a.Time
    ''', (patient_id,)).fetchall()
    
    conn.close()
    
    return render_template('patient/appointments.html', 
                          upcoming=upcoming, 
                          past=past,
                          current_date=current_date)  # Add current_date here

@app.route('/patient/book_appointment', methods=['GET', 'POST'])
def patient_book_appointment():
    if 'user_id' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Add current date
    
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM Doctor').fetchall()
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        time = request.form.get('time')
        purpose = request.form.get('purpose')
        
        if not all([doctor_id, date, time]):
            flash('Doctor, date and time are required', 'error')
        else:
            try:
                conn.execute('''
                INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose) 
                VALUES (?, ?, ?, ?, ?)
                ''', (patient_id, doctor_id, date, time, purpose))
                
                # Check if there's already a doctor-patient relationship
                relationship = conn.execute('''
                SELECT * FROM DoctorPatient WHERE DoctorID = ? AND PatientID = ?
                ''', (doctor_id, patient_id)).fetchone()
                
                # If not, create one
                if not relationship:
                    conn.execute('''
                    INSERT INTO DoctorPatient (DoctorID, PatientID) 
                    VALUES (?, ?)
                    ''', (doctor_id, patient_id))
                
                conn.commit()
                flash('Appointment booked successfully', 'success')
                return redirect(url_for('patient_appointments'))
            
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    conn.close()
    
    return render_template('patient/book_appointment.html', doctors=doctors, current_date=current_date)


@app.route('/patient/medical_records')
def patient_medical_records():
    if 'user_id' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    
    conn = get_db_connection()
    
    records = conn.execute('''
    SELECT mr.*, d.Name as DoctorName 
    FROM MedicalRecord mr 
    JOIN Doctor d ON mr.PrescribedBy = d.DoctorID 
    WHERE mr.PatientID = ? 
    ORDER BY mr.RecordDate DESC
    ''', (patient_id,)).fetchall()
    
    conn.close()
    
    return render_template('patient/medical_records.html', records=records)

@app.route('/patient/diagnoses')
def patient_diagnoses():
    if 'user_id' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))
    
    patient_id = session['user_id']
    
    conn = get_db_connection()
    
    diagnoses = conn.execute('''
    SELECT d.*, doc.Name as DoctorName 
    FROM Diagnosis d 
    JOIN Doctor doc ON d.DiagnosedBy = doc.DoctorID 
    WHERE d.PatientID = ? 
    ORDER BY d.Date DESC
    ''', (patient_id,)).fetchall()
    
    conn.close()
    
    return render_template('patient/diagnoses.html', diagnoses=diagnoses)

if __name__ == '__main__':
    app.run(debug=True)