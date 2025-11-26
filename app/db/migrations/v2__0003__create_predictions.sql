CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    prediction JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX(user_id),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
