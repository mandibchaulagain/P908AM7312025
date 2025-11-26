CREATE TABLE IF NOT EXISTS metric_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    data_type ENUM('float','int','string') NOT NULL DEFAULT 'float',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
