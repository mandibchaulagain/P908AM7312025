-- created table for crop's properties, store prediction
CREATE TABLE IF NOT EXISTS crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nitrogen DECIMAL(10,2) NOT NULL,
    phosphorous DECIMAL(10,2) NOT NULL,
    potassium DECIMAL(10,2) NOT NULL,
    rainfall DECIMAL(10,2) NOT NULL,
    temperature DECIMAL(10,2) NOT NULL,
    humidity DECIMAL(10,2) NOT NULL,
    prediction VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);