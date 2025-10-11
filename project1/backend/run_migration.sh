#!/bin/bash
# Run database migration for Story 3.1

export DATABASE_URL="postgresql://neondb_owner:npg_hAgXDHFnx0q8@ep-blue-band-ag7uu3nh-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require"

python3 << 'EOF'
import os
import sys

# Add api directory to path so we can import database
sys.path.insert(0, 'api')

try:
    from database import db

    # Check if table exists
    import psycopg2
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'app_settings');")
    exists = cur.fetchone()[0]

    if exists:
        print('✓ app_settings table already exists')

        # Check if setting exists
        cur.execute("SELECT value FROM app_settings WHERE key = 'suggestion_engine'")
        result = cur.fetchone()
        if result:
            print(f'✓ suggestion_engine setting exists with value: {result[0]}')
        else:
            print('⚠️  Adding missing suggestion_engine setting...')
            cur.execute("INSERT INTO app_settings (key, value, description) VALUES ('suggestion_engine', 'template', 'Active suggestion engine: template or koop')")
            conn.commit()
            print('✓ Default setting inserted')
    else:
        print('Creating app_settings table...')

        cur.execute("""
            CREATE TABLE app_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("INSERT INTO app_settings (key, value, description) VALUES ('suggestion_engine', 'template', 'Active suggestion engine: template or koop')")

        conn.commit()
        print('✓ app_settings table created successfully')
        print('✓ Default setting inserted: suggestion_engine = template')

    cur.close()
    conn.close()

    print('\n✅ Migration completed successfully!')

except Exception as e:
    print(f'\n❌ Migration failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
