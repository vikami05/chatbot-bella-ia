-- Base de datos para AI Booking Assistant
-- MySQL 8.0+

CREATE DATABASE IF NOT EXISTS booking_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE booking_db;

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    client_phone VARCHAR(20),
    client_email VARCHAR(100),
    service VARCHAR(50) NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    duration INT NOT NULL COMMENT 'Duración en minutos',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, confirmed, cancelled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT,
    INDEX idx_date (booking_date),
    INDEX idx_status (status),
    INDEX idx_client (client_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos de ejemplo (opcional)
INSERT INTO bookings (client_name, client_phone, service, booking_date, booking_time, duration, status) 
VALUES 
    ('María García', '+54911234567', 'corte', '2026-05-10', '14:00:00', 30, 'confirmed'),
    ('Juan Pérez', '+54911234568', 'tintura', '2026-05-11', '10:00:00', 90, 'confirmed'),
    ('Ana López', '+54911234569', 'manicura', '2026-05-10', '16:00:00', 45, 'pending');
