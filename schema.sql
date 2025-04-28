-- PostgreSQL Schema for ClimbUp Solutions Booking System

-- Users table (clients and consultants)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'consultant', 'admin')),
    is_preferred BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Consultants table (extends users)
CREATE TABLE consultants (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    specialization VARCHAR(100) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    availability JSONB NOT NULL,
    max_daily_sessions INTEGER DEFAULT 8,
    is_active BOOLEAN DEFAULT TRUE
);

-- Appointments table
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES users(id),
    consultant_id INTEGER REFERENCES consultants(user_id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('pending', 'paid', 'verified', 'failed')),
    payment_proof_url VARCHAR(255),
    is_peak_hour BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_time_slot CHECK (end_time > start_time)
);

-- Slot holds table (for 15-minute holds)
CREATE TABLE slot_holds (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(id),
    client_id INTEGER REFERENCES users(id),
    consultant_id INTEGER REFERENCES consultants(user_id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'expired', 'converted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_appointments_client ON appointments(client_id);
CREATE INDEX idx_appointments_consultant ON appointments(consultant_id);
CREATE INDEX idx_appointments_time ON appointments(start_time, end_time);
CREATE INDEX idx_slot_holds_time ON slot_holds(start_time, end_time);
CREATE INDEX idx_users_role ON users(role); 