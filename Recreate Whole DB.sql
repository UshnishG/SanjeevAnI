-- Step 1: Create the database
DROP DATABASE IF EXISTS hospital_management;
CREATE DATABASE hospital_management;
USE hospital_management;

-- Step 2: Create Admin table
CREATE TABLE IF NOT EXISTS Admin (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    FullName VARCHAR(255) NOT NULL,
    LastLogin DATETIME,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Step 3: Create Doctor table
CREATE TABLE IF NOT EXISTS Doctor (
    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Specialisation VARCHAR(255) NOT NULL,
    Username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    ContactNumber VARCHAR(15),
    Email VARCHAR(255),
    AddedByAdmin INT,
    JoinDate DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (AddedByAdmin) REFERENCES Admin(AdminID)
) ENGINE=InnoDB;

-- Step 4: Create Patient table
CREATE TABLE IF NOT EXISTS Patient (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Age INT CHECK (Age > 0),
    Gender ENUM('Male', 'Female', 'Other'),
    Password VARCHAR(255) NOT NULL,
    ContactNumber VARCHAR(15),
    Email VARCHAR(255),
    Address TEXT,
    MedicalHistory TEXT,
    BloodGroup VARCHAR(5),
    AssignedDoctorID INT,
    RegistrationDate DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (AssignedDoctorID) REFERENCES Doctor(DoctorID)
) ENGINE=InnoDB;

-- Step 5: Create Diagnosis table
CREATE TABLE IF NOT EXISTS Diagnosis (
    DiagnosisID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    Symptoms TEXT NOT NULL,
    Diagnosis TEXT NOT NULL,
    Notes TEXT,
    Date DATE NOT NULL DEFAULT (CURRENT_DATE),
    DiagnosedBy INT NOT NULL,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DiagnosedBy) REFERENCES Doctor(DoctorID)
) ENGINE=InnoDB;

-- Step 6: Create MedicalRecord table
CREATE TABLE IF NOT EXISTS MedicalRecord (
    RecordID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    Diagnosis TEXT NOT NULL,
    Treatment TEXT NOT NULL,
    PrescribedBy INT NOT NULL,
    RecordDate DATE NOT NULL DEFAULT (CURRENT_DATE),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (PrescribedBy) REFERENCES Doctor(DoctorID)
) ENGINE=InnoDB;

-- Step 7: Create Appointment table
CREATE TABLE IF NOT EXISTS Appointment (
    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    Purpose TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
) ENGINE=InnoDB;

-- Step 8: Create DoctorPatient junction table
CREATE TABLE IF NOT EXISTS DoctorPatient (
    DoctorPatientID INT PRIMARY KEY AUTO_INCREMENT,
    DoctorID INT NOT NULL,
    PatientID INT NOT NULL,
    RelationshipStartDate DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    UNIQUE(DoctorID, PatientID)
) ENGINE=InnoDB;

-- Step 9: Insert Indian sample data with plain text passwords (FOR DEVELOPMENT ONLY)

-- Insert Admin records
INSERT INTO Admin (Username, Password, FullName) VALUES 
('admin_aayush', 'admin@123', 'Aayush Mishra'),
('admin_ushnish', 'admin#456', 'Ushnish Ghosal'),
('admin_utsav', 'admin!789', 'Utsav Opal');

-- Insert Doctors
INSERT INTO Doctor (Name, Specialisation, Username, Password, ContactNumber, Email, AddedByAdmin) VALUES 
('Dr. Rajesh Khanna', 'Cardiology', 'dr_rajesh', 'doc@123', '+919876543210', 'dr.rajesh@example.com', 1),
('Dr. Priya Sharma', 'Pediatrics', 'dr_priya', 'pedia#456', '+919765432109', 'dr.priya@example.com', 1),
('Dr. Amit Patel', 'Orthopedics', 'dr_amit', 'ortho789', '+919654321098', 'dr.amit@example.com', 2),
('Dr. Ananya Reddy', 'Neurology', 'dr_ananya', 'neuro101', '+919543210987', 'dr.ananya@example.com', 2);

-- Insert Patients
INSERT INTO Patient (Name, Age, Gender, Password, ContactNumber, Email, Address, MedicalHistory, BloodGroup, AssignedDoctorID) VALUES 
('Rahul Verma', 45, 'Male', 'patient@123', '+919812345678', 'rahul.v@example.com', '12, Green Park, New Delhi', 'Hypertension since 2018', 'B+', 1),
('Neha Gupta', 32, 'Female', 'neha#456', '+919712345678', 'neha.g@example.com', '34, Andheri East, Mumbai', 'Asthma, Allergic rhinitis', 'A+', 2),
('Arjun Singh', 28, 'Male', 'arjun789', '+919612345678', 'arjun.s@example.com', '56, Banjara Hills, Hyderabad', 'Sports injury - ACL tear (2022)', 'O+', 3),
('Sanya Malhotra', 60, 'Female', 'sanya101', '+919512345678', 'sanya.m@example.com', '78, Koramangala, Bangalore', 'Type 2 Diabetes, High cholesterol', 'AB+', 1),
('Vikram Joshi', 52, 'Male', 'vikram@2023', '+919432156789', 'vikram.j@example.com', '90, Civil Lines, Pune', 'Heart disease, Angioplasty (2021)', 'B-', 1);

-- Insert DoctorPatient relationships
INSERT INTO DoctorPatient (DoctorID, PatientID) VALUES 
(1, 1),
(1, 4),
(1, 5),
(2, 2),
(3, 3);

-- Insert Diagnoses
INSERT INTO Diagnosis (PatientID, Symptoms, Diagnosis, Notes, DiagnosedBy) VALUES 
(1, 'High BP, Chest discomfort', 'Hypertension, Possible angina', 'Advise ECG and stress test', 1),
(2, 'Wheezing, Shortness of breath', 'Asthma exacerbation', 'Trigger likely pollen allergy', 2),
(3, 'Knee pain, Swelling', 'ACL injury, Grade 2', 'Recommend MRI for confirmation', 3),
(4, 'Fatigue, Increased thirst', 'Uncontrolled diabetes', 'HbA1c 8.5%', 1),
(5, 'Chest pain, Palpitations', 'Stable angina', 'Continue current medications', 1);

-- Insert MedicalRecords
INSERT INTO MedicalRecord (PatientID, Diagnosis, Treatment, PrescribedBy) VALUES 
(1, 'Hypertension, Possible angina', 'Amlodipine 5mg OD, Lifestyle modifications', 1),
(2, 'Asthma exacerbation', 'Salbutamol inhaler PRN, Montelukast 10mg HS', 2),
(3, 'ACL injury, Grade 2', 'RICE protocol, Physiotherapy, Knee brace', 3),
(4, 'Uncontrolled diabetes', 'Metformin 1000mg BD, Glimepiride 2mg OD', 1),
(5, 'Stable angina', 'Aspirin 75mg OD, Atorvastatin 40mg HS', 1);

-- Insert Appointments
INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose) VALUES 
(1, 1, '2023-07-05', '10:00:00', 'Follow-up for hypertension'),
(2, 2, '2023-07-06', '11:30:00', 'Asthma checkup'),
(3, 3, '2023-07-07', '14:00:00', 'Knee injury follow-up'),
(4, 1, '2023-07-08', '15:30:00', 'Diabetes management'),
(5, 1, '2023-07-10', '09:00:00', 'Cardiac consultation');