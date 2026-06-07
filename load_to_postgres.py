
import json
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values, Json

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', '5432')),
    'dbname': os.getenv('PGDATABASE', 'your_db'),
    'user': os.getenv('PGUSER', 'your_user'),
    'password': os.getenv('PGPASSWORD', 'your_password'),
}

JSON_PATH = Path(__file__).parent / 'data' / 'products.json'

def ensure_tables(cur):
    cur.execute('''
    CREATE TABLE IF NOT EXISTS staging_products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        material TEXT,
        use_case TEXT,
        source TEXT,
        url TEXT,
        technical JSONB,
        keywords JSONB,
        tags JSONB,
        priority INT DEFAULT 0,
        raw JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    ''')

def load_json():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize(item):
    return (
        item.get('name'),
        item.get('category'),
        item.get('material'),
        item.get('use_case'),
        item.get('source'),
        item.get('url'),
        Json(item.get('technical', {})),
        Json(item.get('keywords', [])),
        Json(item.get('tags', [])),
        int(item.get('priority', 0)),
        Json(item),
    )

def main():
    data = load_json()
    rows = [normalize(x) for x in data]
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                ensure_tables(cur)
                execute_values(
                    cur,
                    '''
                    INSERT INTO staging_products
                    (name, category, material, use_case, source, url, technical, keywords, tags, priority, raw)
                    VALUES %s
                    ''',
                    rows,
                    template='(%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s::jsonb)'
                )
        print(f'Inserted {len(rows)} rows into staging_products')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
