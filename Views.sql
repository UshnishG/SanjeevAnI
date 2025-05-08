USE hospital_management;

-- View: Doctor's Patient List
CREATE OR REPLACE VIEW DoctorPatientList AS
SELECT d.DoctorID, d.Name AS DoctorName, p.PatientID, p.Name AS PatientName, p.Age, p.Gender
FROM Doctor d
JOIN DoctorPatient dp ON d.DoctorID = dp.DoctorID
JOIN Patient p ON p.PatientID = dp.PatientID;

-- View: Patient's Full Medical History
CREATE OR REPLACE VIEW PatientFullHistory AS
SELECT p.PatientID, p.Name AS PatientName, d.Name AS DoctorName, mr.Diagnosis, mr.Treatment, mr.RecordDate
FROM MedicalRecord mr
JOIN Patient p ON p.PatientID = mr.PatientID
JOIN Doctor d ON d.DoctorID = mr.PrescribedBy;
