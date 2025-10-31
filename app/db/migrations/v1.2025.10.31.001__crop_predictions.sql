CREATE TABLE IF NOT EXISTS crop_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nitrogen FLOAT NOT NULL,
    phosphorous FLOAT NOT NULL,
    potassium FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    rainfall FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    prediction JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
