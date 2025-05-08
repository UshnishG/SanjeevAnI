use hospital_management;

DELIMITER //

CREATE PROCEDURE GenerateDiagnosisReport(IN p_DoctorID INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE p_name VARCHAR(255);
    DECLARE diag TEXT;

    DECLARE cur CURSOR FOR
        SELECT p.Name, dg.Diagnosis
        FROM Diagnosis dg
        JOIN Patient p ON p.PatientID = dg.PatientID
        WHERE dg.DiagnosedBy = p_DoctorID;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    CREATE TEMPORARY TABLE IF NOT EXISTS TempDiagnosisReport (
        PatientName VARCHAR(255),
        Diagnosis TEXT
    );

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO p_name, diag;
        IF done THEN
            LEAVE read_loop;
        END IF;
        INSERT INTO TempDiagnosisReport VALUES (p_name, diag);
    END LOOP;

    CLOSE cur;

    SELECT * FROM TempDiagnosisReport;
    DROP TEMPORARY TABLE TempDiagnosisReport;
END //

DELIMITER ;
