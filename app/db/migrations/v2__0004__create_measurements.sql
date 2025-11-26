CREATE TABLE IF NOT EXISTS measurements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT NOT NULL,
    metric_id INT NOT NULL,
    value DOUBLE NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX (prediction_id),
    INDEX (metric_id),

    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE,
    FOREIGN KEY (metric_id) REFERENCES metric_types(id)
);
