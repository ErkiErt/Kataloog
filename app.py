
import json
import re
from pathlib import Path
import streamlit as st

st.set_page_config(page_title='Materjalide sobitaja', layout='wide')

DATA = json.loads(Path('data/products.json').read_text(encoding='utf-8'))

def detect_category(text):
    t = text.lower()
    if any(k in t for k in ['akna', 'tihend']): return 'aknatihend'
    if any(k in t for k in ['terrass', 'puidu alla', 'tuulutus']): return 'terrass'
    if any(k in t for k in ['sadam', 'kai', 'fender', 'vender']): return 'sadam'
    if any(k in t for k in ['betoon', 'ehitus', 'vuuk', 'läbiviik']): return 'ehitus'
    return 'aknatihend'

def tokenize(text):
    return set(re.findall(r"[\wäöõüšž-]+", text.lower()))

def score_item(text, item, cat):
    toks = tokenize(text)
    s = 0
    if item['category'] == cat:
        s += 50
    if any(tag in toks for tag in item.get('tags', [])):
        s += 25
    if any(k in text.lower() for k in item.get('keywords', [])):
        s += 15
    if item.get('source'):
        s += 5
    return s + int(item.get('priority', 0))

st.title('Nutikas materjalisoovitus')
q = st.text_input('Kirjuta, mida vajad', placeholder='nt aknatihendit vaja')

if q:
    cat = detect_category(q)
    results = [
        (score_item(q, item, cat), item)
        for item in DATA
        if item['category'] == cat
    ]
    results.sort(key=lambda x: (-x[0], x[1]['name']))
    st.subheader(f'Sobiv kategooria: {cat}')
    for i, (sc, item) in enumerate(results, 1):
        st.write(f"{i}. {item['name']} — skoor {sc}")
        st.caption(f"Materjal: {item['material']} | Kasutus: {item['use_case']}")
        st.caption(f"Allikas: {item['source']}")
