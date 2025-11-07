-- Fix database schema for leads table
-- Add missing columns that exist in the model but not in the database

-- Remove lead_id column if it exists (it's not in the current model)
-- ALTER TABLE leads DROP COLUMN IF EXISTS lead_id;

-- Add consultation-related columns if they don't exist
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_requested BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_booked BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_type VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_challenges TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_scheduled_at TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_completed_at TIMESTAMP;

-- Add AI report related columns if they don't exist
ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_requested BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_generated BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_id VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_generated_at TIMESTAMP;

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'leads' 
ORDER BY ordinal_position;
