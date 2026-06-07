
# Material Match Real Data App

## Käivitamine
1. Installi sõltuvused:
   ```bash
   pip install -r requirements.txt
   ```
2. Käivita rakendus:
   ```bash
   streamlit run app.py
   ```

## Mida testida
- `aknatihendit vaja`
- `terrassile puidu alla kummi`
- `sadamasse fenderit vaja`
- `betooni vuugi tihend`

## Andmeallikad
Tooted on näidatud allikate põhjal:
- Zenith Europe Manticore Eco
- Zenith Europe EPDM datasheet
- Quadrofixing terrace pads
- DD Group SBR rubber pads
- Trelleborg marine fenders
- Construction joint seals guide


## PostgreSQL import
Run the loader:
```bash
python load_to_postgres.py
```

Environment variables:
- PGHOST
- PGPORT
- PGDATABASE
- PGUSER
- PGPASSWORD


## Normalization to PostgreSQL tables
1. Create schema:
```bash
psql -d your_db -f schema_normalize.sql
```
2. Load JSON into staging:
```bash
python load_to_postgres.py
```
3. Normalize into final tables:
```bash
python normalize_to_pg.py
```
