use hospital_management;
DELIMITER //

-- Function: Total patients assigned to a doctor
CREATE FUNCTION GetAssignedPatientCount(p_DoctorID INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE countPatients INT;
    SELECT COUNT(*) INTO countPatients
    FROM DoctorPatient
    WHERE DoctorID = p_DoctorID;
    RETURN countPatients;
END //

DELIMITER ;
