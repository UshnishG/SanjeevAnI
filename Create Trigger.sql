use hospital_management;


ALTER TABLE Doctor ADD COLUMN LastAppointmentDate DATE;

DELIMITER //

CREATE TRIGGER UpdateLastAppointment
AFTER INSERT ON Appointment
FOR EACH ROW
BEGIN
    UPDATE Doctor
    SET LastAppointmentDate = NEW.Date
    WHERE DoctorID = NEW.DoctorID;
END //

DELIMITER ;
