
import re
import streamlit as st

st.set_page_config(page_title='Materjalide sobitaja', layout='wide')

CATALOG = [
    {"name": "EPDM aknatihend", "category": "aknatihend", "material": "EPDM", "tags": ["uv", "ilmastik", "tihend"], "score": 95},
    {"name": "Silicone aknatihend", "category": "aknatihend", "material": "Silicone", "tags": ["kuumus", "paindlik", "tihend"], "score": 85},
    {"name": "SBR terrassipadi", "category": "terrass", "material": "SBR", "tags": ["puit", "tuulutus", "aluskumm", "niiskus"], "score": 90},
    {"name": "EPDM terrassipadi", "category": "terrass", "material": "EPDM", "tags": ["puit", "tuulutus", "aluskumm", "ilmastik"], "score": 88},
    {"name": "Marine fender standard", "category": "sadam", "material": "Kumm", "tags": ["fender", "kai", "löögikaitse"], "score": 98},
    {"name": "Betoonivuugi tihend", "category": "ehitus", "material": "EPDM", "tags": ["vuuk", "läbiviik", "veekindel"], "score": 92},
]

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
    if item['category'] == cat: s += 40
    if any(tag in toks for tag in item['tags']): s += 35
    if item['material'].lower() in toks: s += 10
    s += min(item['score'] // 2, 10)
    return s

st.title('Nutikas materjalisoovitus')
query = st.text_input('Kirjuta, mida vajad', placeholder='nt aknatihendit vaja')

if query:
    cat = detect_category(query)
    results = []
    for item in CATALOG:
        if item['category'] != cat:
            continue
        results.append((score_item(query, item, cat), item))
    results.sort(key=lambda x: (-x[0], -x[1]['score'], x[1]['name']))
    st.subheader(f'Sobiv kategooria: {cat}')
    for i, (sc, item) in enumerate(results[:5], 1):
        st.write(f"{i}. {item['name']} — skoor {sc}")
        st.caption(f"Materjal: {item['material']} | Märksõnad: {', '.join(item['tags'])}")
    if not results:
        st.warning('Sobivaid tulemusi ei leitud.')
