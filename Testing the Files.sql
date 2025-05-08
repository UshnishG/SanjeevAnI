use hospital_management;


show tables;

-- Test Sample Data
SELECT * FROM Admin;
SELECT * FROM Doctor;
SELECT * FROM Patient;
SELECT * FROM Appointment;

-- Test View: DoctorPatientList
SELECT * FROM DoctorPatientList;

-- Test View: PatientFullHistory
SELECT * FROM PatientFullHistory;

-- Test Stored Procedure
CALL BookAppointment(1, 2, '2025-04-20', '10:00:00', 'Follow-up checkup');

SELECT * FROM Appointment WHERE PatientID = 1 AND DoctorID = 2 ORDER BY AppointmentID DESC;

CALL GetDoctorAppointments(1);

-- Test Function
SELECT GetAssignedPatientCount(1) AS PatientCount;

-- Test Trigger
DESC Doctor;
INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose)
VALUES (2, 1, '2025-04-21', '11:00:00', 'Test Trigger Update');
SELECT LastAppointmentDate FROM Doctor WHERE DoctorID = 1;

-- Test cursor

CALL GenerateDiagnosisReport(1);
-- Patients with either Appointments or Records
SELECT p.PatientID, p.Name 
FROM Patient p
WHERE EXISTS (SELECT 1 FROM Appointment a WHERE a.PatientID = p.PatientID)
UNION
SELECT p.PatientID, p.Name 
FROM Patient p
WHERE EXISTS (SELECT 1 FROM MedicalRecord mr WHERE mr.PatientID = p.PatientID);

-- Patients with both Appointments and Records
SELECT p.PatientID, p.Name 
FROM Patient p
WHERE EXISTS (SELECT 1 FROM Appointment a WHERE a.PatientID = p.PatientID)
  AND EXISTS (SELECT 1 FROM MedicalRecord mr WHERE mr.PatientID = p.PatientID);





