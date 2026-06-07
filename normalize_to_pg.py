
import json
import os
from pathlib import Path
import psycopg2

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', '5432')),
    'dbname': os.getenv('PGDATABASE', 'your_db'),
    'user': os.getenv('PGUSER', 'your_user'),
    'password': os.getenv('PGPASSWORD', 'your_password'),
}

BASE = Path(__file__).parent
PRODUCTS = json.loads((BASE / 'data' / 'products.json').read_text(encoding='utf-8'))

CATEGORY_MAP = {
    'aknatihend': ('window', 'Aknatihendid'),
    'terrass': ('terrace', 'Terrass'),
    'sadam': ('marine', 'Sadam / marine'),
    'ehitus': ('construction', 'Ehitus'),
}

def connect():
    return psycopg2.connect(**DB_CONFIG)

def upsert_category(cur, code, name):
    cur.execute(
        'INSERT INTO categories (code, name) VALUES (%s, %s) ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name RETURNING id',
        (code, name)
    )
    return cur.fetchone()[0]

def upsert_use_case(cur, code, name, desc):
    cur.execute(
        'INSERT INTO use_cases (code, name, description) VALUES (%s, %s, %s) ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description RETURNING id',
        (code, name, desc)
    )
    return cur.fetchone()[0]

def upsert_material(cur, code, name, category_id, desc):
    cur.execute(
        'INSERT INTO materials (code, name, category_id, description) VALUES (%s, %s, %s, %s) ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id, description = EXCLUDED.description RETURNING id',
        (code, name, category_id, desc)
    )
    return cur.fetchone()[0]

def main():
    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                for code, name in CATEGORY_MAP.values():
                    upsert_category(cur, code, name)

                uc_ids = {
                    'aknatihend': upsert_use_case(cur, 'aknatihend', 'Aknatihend', 'Välis- ja aknatihendite soovitused'),
                    'terrass': upsert_use_case(cur, 'terrass', 'Terrass', 'Terrassi aluskummid ja tuulutuspadjad'),
                    'sadam': upsert_use_case(cur, 'sadam', 'Sadam', 'Marine fender lahendused'),
                    'ehitus': upsert_use_case(cur, 'ehitus', 'Ehitus', 'Betooni ja vuukide tihendid'),
                }

                category_ids = {}
                cur.execute('SELECT id, code FROM categories')
                for cid, code in cur.fetchall():
                    category_ids[code] = cid

                for p in PRODUCTS:
                    cat_code, _ = CATEGORY_MAP[p['category']]
                    material_code = p['name'].lower().replace(' ', '_').replace('/', '_')[:80]
                    mid = upsert_material(cur, material_code, p['name'], category_ids[cat_code], p.get('use_case'))
                    tech = p.get('technical', {})
                    cur.execute(
                        '''
                        INSERT INTO material_properties
                        (material_id, temperature_min, temperature_max, hardness_shore_a, compression_set, tensile_strength_mpa, elongation_at_break_pct, uv_resistance, ozone_resistance, abrasion_resistance, energy_absorption, reaction_force, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',
                        (
                            mid,
                            tech.get('min_temperature'),
                            tech.get('max_temperature'),
                            tech.get('hardness_shore_a'),
                            tech.get('compression_set'),
                            tech.get('tensile_strength_mpa'),
                            tech.get('elongation_break_pct'),
                            tech.get('uv_resistance'),
                            tech.get('ozone_resistance'),
                            tech.get('abrasion_resistance'),
                            tech.get('energy_absorption'),
                            tech.get('reaction_force'),
                            json.dumps(tech, ensure_ascii=False),
                        )
                    )
        print('Normalization complete')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
