CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone_number VARCHAR(20),
    password VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE
);