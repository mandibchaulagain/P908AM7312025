ALTER TABLE users
MODIFY COLUMN role ENUM('user', 'admin') NOT NULL DEFAULT 'user';