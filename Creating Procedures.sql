USE hospital_management;
DELIMITER //

-- Procedure to book appointment
CREATE PROCEDURE BookAppointment (
    IN p_PatientID INT,
    IN p_DoctorID INT,
    IN p_Date DATE,
    IN p_Time TIME,
    IN p_Purpose TEXT
)
BEGIN
    INSERT INTO Appointment (PatientID, DoctorID, Date, Time, Purpose)
    VALUES (p_PatientID, p_DoctorID, p_Date, p_Time, p_Purpose);
    SELECT 'Appointment booked successfully' AS Message;
END //

-- Procedure to get all upcoming appointments for a doctor
CREATE PROCEDURE GetDoctorAppointments (IN p_DoctorID INT)
BEGIN
    SELECT a.AppointmentID, p.Name AS PatientName, a.Date, a.Time, a.Status, a.Purpose
    FROM Appointment a
    JOIN Patient p ON p.PatientID = a.PatientID
    WHERE a.DoctorID = p_DoctorID AND a.Date >= CURDATE()
    ORDER BY a.Date, a.Time;
END //

DELIMITER ;
