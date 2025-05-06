# Hospital Management System Routes Documentation

This document provides a comprehensive explanation of all routes in the Hospital Management System, along with their corresponding SQL operations.

## Authentication Routes

### `/login` (GET, POST)
- **Purpose**: General login route for all user types
- **SQL Operations**: 
  - Query Admin, Doctor, or Patient tables based on user type
  - Check password hash against stored password
  - Update last login timestamp for admin users
- **Authentication**: Creates session with user_id, user_type, and username

### `/login/patient` (GET, POST)
- **Purpose**: Specific login route for patients
- **SQL Operations**: 
  - `SELECT * FROM Patient WHERE Email = ?`
  - Verify password hash
- **Authentication**: Creates patient-specific session

### `/login/doctor` (GET, POST)
- **Purpose**: Specific login route for doctors
- **SQL Operations**: 
  - `SELECT * FROM Doctor WHERE Username = ?`
  - Verify password hash
- **Authentication**: Creates doctor-specific session

### `/login/admin` (GET, POST)
- **Purpose**: Specific login route for administrators
- **SQL Operations**: 
  - `SELECT * FROM Admin WHERE Username = ?` 
  - `UPDATE Admin SET LastLogin = ? WHERE AdminID = ?`
  - Verify password hash
- **Authentication**: Creates admin-specific session

### `/logout` (GET)
- **Purpose**: Ends user session
- **SQL Operations**: None
- **Authentication**: Clears session data

## Dashboard Route

### `/dashboard` (GET)
- **Purpose**: Display dashboard based on user type
- **SQL Operations**:
  - **Admin**:
    - `SELECT * FROM Doctor`
    - `SELECT * FROM Patient`
    - `SELECT a.*, p.Name as PatientName, d.Name as DoctorName FROM Appointment a JOIN Patient p JOIN Doctor d`
  - **Doctor**:
    - `SELECT * FROM Doctor WHERE DoctorID = ?`
    - `SELECT p.* FROM Patient p JOIN DoctorPatient dp WHERE dp.DoctorID = ?`
    - `SELECT a.*, p.Name as PatientName FROM Appointment a JOIN Patient p WHERE a.DoctorID = ? AND a.Status = 'Scheduled' AND a.Date >= date('now')`
  - **Patient**:
    - `SELECT * FROM Patient WHERE PatientID = ?`
    - `SELECT * FROM Doctor WHERE DoctorID = ?` (for assigned doctor)
    - `SELECT a.*, d.Name as DoctorName FROM Appointment a JOIN Doctor d WHERE a.PatientID = ?`
    - `SELECT mr.*, d.Name as DoctorName FROM MedicalRecord mr JOIN Doctor d WHERE mr.PatientID = ?`
    - `SELECT diag.*, d.Name as DoctorName FROM Diagnosis diag JOIN Doctor d WHERE diag.PatientID = ?`

## Admin Routes

### `/admin/doctors` (GET)
- **Purpose**: View list of all doctors
- **SQL Operations**: `SELECT * FROM Doctor`
- **Authentication**: Requires admin session

### `/admin/add_doctor` (GET, POST)
- **Purpose**: Add a new doctor to the system
- **SQL Operations**:
  - Check for existing username: `SELECT * FROM Doctor WHERE Username = ?`
  - Insert new doctor: `INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) VALUES (?, ?, ?, ?, ?, ?, ?)`
- **Authentication**: Requires admin session

### `/admin/patients` (GET)
- **Purpose**: View list of all patients
- **SQL Operations**: `SELECT p.*, d.Name as DoctorName FROM Patient p LEFT JOIN Doctor d ON p.AssignedDoctorID = d.DoctorID`
- **Authentication**: Requires admin session

### `/admin/add_patient` (GET, POST)
- **Purpose**: Add a new patient to the system
- **SQL Operations**:
  - Insert patient: `INSERT INTO Patient (Name, Age, Gender, Password, ContactNumber, Email, Address, MedicalHistory, BloodGroup, AssignedDoctorID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  - Create doctor-patient relationship: `INSERT INTO DoctorPatient (DoctorID, PatientID) VALUES (?, ?)`
- **Authentication**: Requires admin session

### `/admin/edit_appointment/<int:appointment_id>` (GET, POST)
- **Purpose**: Edit an existing appointment
- **SQL Operations**:
  - Get appointment details: `SELECT a.*, p.Name as PatientName, d.Name as DoctorName FROM Appointment a JOIN Patient p JOIN Doctor d WHERE a.AppointmentID = ?`
  - Get doctors and patients: `SELECT * FROM Doctor` and `SELECT * FROM Patient`
  - Update appointment: `UPDATE Appointment SET DoctorID = ?, PatientID = ?, Date = ?, Time = ?, Status = ?, Purpose = ? WHERE AppointmentID = ?`
- **Authentication**: Requires admin session

## Doctor Routes

### `/doctor/patients` (GET)
- **Purpose**: View patients assigned to the doctor
- **SQL Operations**: `SELECT p.* FROM Patient p JOIN DoctorPatient dp ON p.PatientID = dp.PatientID WHERE dp.DoctorID = ?`
- **Authentication**: Requires doctor session

### `/doctor/patient/<int:patient_id>` (GET)
- **Purpose**: View detailed information about a specific patient
- **SQL Operations**:
  - Check doctor-patient relationship: `SELECT * FROM DoctorPatient WHERE DoctorID = ? AND PatientID = ?`
  - Get patient details: `SELECT * FROM Patient WHERE PatientID = ?`
  - Get diagnoses: `SELECT * FROM Diagnosis WHERE PatientID = ? AND DiagnosedBy = ? ORDER BY Date DESC`
  - Get medical records: `SELECT * FROM MedicalRecord WHERE PatientID = ? AND PrescribedBy = ? ORDER BY RecordDate DESC`
  - Get appointments: `SELECT * FROM Appointment WHERE PatientID = ? AND DoctorID = ? ORDER BY Date DESC, Time`
- **Authentication**: Requires doctor session

### `/doctor/add_diagnosis/<int:patient_id>` (GET, POST)
- **Purpose**: Add a diagnosis for a patient
- **SQL Operations**:
  - Get patient: `SELECT * FROM Patient WHERE PatientID = ?`
  - Insert diagnosis: `INSERT INTO Diagnosis (PatientID, Symptoms, Diagnosis, Notes, Date, DiagnosedBy) VALUES (?, ?, ?, ?, ?, ?)`
- **Authentication**: Requires doctor session

### `/doctor/edit_diagnosis/<int:diagnosis_id>` (GET, POST)
- **Purpose**: Edit an existing diagnosis
- **SQL Operations**:
  - Get diagnosis: `SELECT d.*, p.Name as PatientName FROM Diagnosis d JOIN Patient p ON d.PatientID = p.PatientID WHERE d.DiagnosisID = ? AND d.DiagnosedBy = ?`
  - Update diagnosis: `UPDATE Diagnosis SET Symptoms = ?, Diagnosis = ?, Notes = ?, Date = ? WHERE DiagnosisID = ? AND DiagnosedBy = ?`
- **Authentication**: Requires doctor session

### `/doctor/add_medical_record/<int:patient_id>` (GET, POST)
- **Purpose**: Add a medical record for a patient
- **SQL Operations**:
  - Get patient: `SELECT * FROM Patient WHERE PatientID = ?`
  - Insert record: `INSERT INTO MedicalRecord (PatientID, Diagnosis, Treatment, RecordDate, PrescribedBy) VALUES (?, ?, ?, ?, ?)`
- **Authentication**: Requires doctor session

### `/doctor/appointments` (GET)
- **Purpose**: View doctor's appointments
- **SQL Operations**:
  - Get upcoming appointments: `SELECT a.*, p.Name as PatientName FROM Appointment a JOIN Patient p WHERE a.DoctorID = ? AND a.Status = 'Scheduled' AND a.Date >= date('now')`
  - Get past appointments: `SELECT a.*, p.Name as PatientName FROM Appointment a JOIN Patient p WHERE a.DoctorID = ? AND (a.Status != 'Scheduled' OR a.Date < date('now'))`
- **Authentication**: Requires doctor session

### `/doctor/add_appointment` (GET, POST)
- **Purpose**: Add a new appointment for a patient
- **SQL Operations**:
  - Get patients: `SELECT p.* FROM Patient p JOIN DoctorPatient dp ON p.PatientID = dp.PatientID WHERE dp.DoctorID = ?`
  - Insert appointment: `INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose) VALUES (?, ?, ?, ?, ?)`
- **Authentication**: Requires doctor session

### `/doctor/update_appointment/<int:appointment_id>` (POST)
- **Purpose**: Update the status of an appointment
- **SQL Operations**:
  - Verify appointment: `SELECT * FROM Appointment WHERE AppointmentID = ? AND DoctorID = ?`
  - Update status: `UPDATE Appointment SET Status = ? WHERE AppointmentID = ?`
- **Authentication**: Requires doctor session

### `/doctor/calendar` (GET)
- **Purpose**: View appointments in a calendar format
- **SQL Operations**:
  - Get doctor info: `SELECT * FROM Doctor WHERE DoctorID = ?`
  - Get appointments: `SELECT a.*, p.Name as PatientName FROM Appointment a JOIN Patient p ON a.PatientID = p.PatientID WHERE a.DoctorID = ? ORDER BY a.Date, a.Time`
- **Authentication**: Requires doctor session

### `/doctor/edit_profile` (GET, POST)
- **Purpose**: Edit doctor's profile information
- **SQL Operations**:
  - Get doctor: `SELECT * FROM Doctor WHERE DoctorID = ?`
  - Update profile: `UPDATE Doctor SET ContactNumber = ?, Email = ?, Specialisation = ? WHERE DoctorID = ?`
- **Authentication**: Requires doctor session

## Patient Routes

### `/patient/profile` (GET)
- **Purpose**: View patient profile information
- **SQL Operations**:
  - Get patient: `SELECT * FROM Patient WHERE PatientID = ?`
  - Get assigned doctor: `SELECT * FROM Doctor WHERE DoctorID = ?`
- **Authentication**: Requires patient session

### `/patient/edit_profile` (GET, POST)
- **Purpose**: Edit patient profile information
- **SQL Operations**:
  - Get patient: `SELECT * FROM Patient WHERE PatientID = ?`
  - Update profile: `UPDATE Patient SET ContactNumber = ?, Email = ?, Address = ?, MedicalHistory = ? WHERE PatientID = ?`
- **Authentication**: Requires patient session

### `/patient/appointments` (GET)
- **Purpose**: View patient's appointments
- **SQL Operations**:
  - Get upcoming appointments: `SELECT a.*, d.Name as DoctorName, d.Specialisation as DoctorSpecialisation FROM Appointment a JOIN Doctor d WHERE a.PatientID = ? AND a.Status = 'Scheduled' AND a.Date >= date('now')`
  - Get past appointments: `SELECT a.*, d.Name as DoctorName, d.Specialisation as DoctorSpecialisation FROM Appointment a JOIN Doctor d WHERE a.PatientID = ? AND (a.Status != 'Scheduled' OR a.Date < date('now'))`
- **Authentication**: Requires patient session

### `/patient/book_appointment` (GET, POST)
- **Purpose**: Book a new appointment with a doctor
- **SQL Operations**:
  - Get doctors: `SELECT * FROM Doctor`
  - Insert appointment: `INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose) VALUES (?, ?, ?, ?, ?)`
  - Check relationship: `SELECT * FROM DoctorPatient WHERE DoctorID = ? AND PatientID = ?`
  - Create relationship if needed: `INSERT INTO DoctorPatient (DoctorID, PatientID) VALUES (?, ?)`
- **Authentication**: Requires patient session

### `/patient/medical_records` (GET)
- **Purpose**: View patient's medical records
- **SQL Operations**: `SELECT mr.*, d.Name as DoctorName FROM MedicalRecord mr JOIN Doctor d ON mr.PrescribedBy = d.DoctorID WHERE mr.PatientID = ? ORDER BY mr.RecordDate DESC`
- **Authentication**: Requires patient session

### `/patient/diagnoses` (GET)
- **Purpose**: View patient's diagnoses
- **SQL Operations**: `SELECT d.*, doc.Name as DoctorName FROM Diagnosis d JOIN Doctor doc ON d.DiagnosedBy = doc.DoctorID WHERE d.PatientID = ? ORDER BY d.Date DESC`
- **Authentication**: Requires patient session

## Utility Routes

### `/change_password` (GET, POST)
- **Purpose**: Change password for any user type
- **SQL Operations**:
  - Get user based on type: 
    - Admin: `SELECT * FROM Admin WHERE AdminID = ?`
    - Doctor: `SELECT * FROM Doctor WHERE DoctorID = ?`
    - Patient: `SELECT * FROM Patient WHERE PatientID = ?`
  - Update password: `UPDATE {table} SET Password = ? WHERE {id_column} = ?`
- **Authentication**: Requires valid session

### `/chatbot` (POST)
- **Purpose**: API endpoint for medical chatbot responses
- **SQL Operations**: 
  - For patients: `SELECT * FROM Patient WHERE PatientID = ?` (to get patient context)
  - Uses Gemini AI model to generate responses
- **Authentication**: Requires valid session

## Database Schema Overview

The system uses the following tables:
- **Admin**: Stores administrator information (AdminID, Username, Password, FullName, LastLogin)
- **Doctor**: Stores doctor information (DoctorID, Name, Specialisation, Username, Password, ContactNumber, Email)
- **Patient**: Stores patient information (PatientID, Name, Age, Gender, Password, ContactNumber, Email, Address, MedicalHistory, BloodGroup, AssignedDoctorID)
- **Diagnosis**: Stores patient diagnoses (DiagnosisID, PatientID, Symptoms, Diagnosis, Notes, Date, DiagnosedBy)
- **MedicalRecord**: Stores medical records (RecordID, PatientID, Diagnosis, Treatment, PrescribedBy, RecordDate)
- **Appointment**: Stores appointment information (AppointmentID, PatientID, DoctorID, Date, Time, Status, Purpose)
- **DoctorPatient**: Junction table relating doctors to patients (DoctorPatientID, DoctorID, PatientID)

This comprehensive system provides role-specific functionality for administrators, doctors, and patients, with proper authentication and authorization mechanisms in place.
