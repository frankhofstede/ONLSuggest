#!/usr/bin/env python
"""
Manually run the app_settings migration
Epic 3 Story 3.1
"""
import os
import psycopg2

# Load DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Try to load from .env
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    DATABASE_URL = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        pass

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in environment or .env file")
    exit(1)

print(f"Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check if app_settings table already exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'app_settings');")
    exists = cur.fetchone()[0]

    if exists:
        print('✓ app_settings table already exists')

        # Check if default setting exists
        cur.execute("SELECT value FROM app_settings WHERE key = 'suggestion_engine'")
        result = cur.fetchone()
        if result:
            print(f'✓ suggestion_engine setting exists with value: {result[0]}')
        else:
            print('⚠️  app_settings table exists but suggestion_engine setting missing')
            cur.execute("INSERT INTO app_settings (key, value, description) VALUES ('suggestion_engine', 'template', 'Active suggestion engine: template or koop')")
            conn.commit()
            print('✓ Default setting inserted')
    else:
        print('Creating app_settings table...')

        # Create app_settings table
        cur.execute("""
            CREATE TABLE app_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert default setting
        cur.execute("INSERT INTO app_settings (key, value, description) VALUES ('suggestion_engine', 'template', 'Active suggestion engine: template or koop')")

        conn.commit()
        print('✓ app_settings table created successfully')
        print('✓ Default setting inserted: suggestion_engine = template')

    cur.close()
    conn.close()

    print('\n✅ Migration completed successfully!')

except Exception as e:
    print(f'\n❌ Migration failed: {e}')
    exit(1)
