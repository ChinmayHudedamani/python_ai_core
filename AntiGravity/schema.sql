-- Neon Serverless PostgreSQL Database Schema

-- 1. Appointments Ledger Table
CREATE TABLE IF NOT EXISTS appointments_ledger (
    id UUID PRIMARY KEY,
    patient_number VARCHAR(50) NOT NULL,
    time_slot VARCHAR(150) NOT NULL UNIQUE,
    procedure_type VARCHAR(100) NOT NULL,
    transaction_id VARCHAR(100) NOT NULL,
    sha256_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes for Appointments
CREATE INDEX IF NOT EXISTS idx_appointments_ledger_patient ON appointments_ledger(patient_number);
CREATE INDEX IF NOT EXISTS idx_appointments_ledger_created ON appointments_ledger(created_at DESC);

-- 2. Conversation Transcripts Store Table
CREATE TABLE IF NOT EXISTS conversation_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE_AUTOMATED',
    total_turns INT DEFAULT 0,
    turns_data JSONB DEFAULT '[]'::jsonb,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversation_transcripts(phone);

-- 3. Telemetry & Analytics Events Table
CREATE TABLE IF NOT EXISTS telemetry_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name VARCHAR(100) NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
