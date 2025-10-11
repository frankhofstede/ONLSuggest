-- Check if app_settings table exists
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_name = 'app_settings'
) AS table_exists;

-- Create table if it doesn't exist (run manually if needed)
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default setting if it doesn't exist
INSERT INTO app_settings (key, value, description) 
VALUES ('suggestion_engine', 'template', 'Active suggestion engine: template or koop')
ON CONFLICT (key) DO NOTHING;

-- Show current settings
SELECT * FROM app_settings;
