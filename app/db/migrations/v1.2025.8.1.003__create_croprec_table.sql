CREATE TABLE IF NOT EXISTS crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nitrogen FLOAT NOT NULL,
    phosphorous FLOAT NOT NULL,
    potassium FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    rainfall FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    prediction VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);