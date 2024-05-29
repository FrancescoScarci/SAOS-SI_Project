DROP DATABASE IF EXISTS flask_app;

CREATE DATABASE IF NOT EXISTS flask_app;

USE flask_app;

CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    uploaded_by VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';


GRANT INSERT ON flask_app.files TO 'username'@'localhost';
GRANT SELECT ON flask_app.files TO 'username'@'localhost';