
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Zenithi assistent", layout="wide")
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

@st.cache_data
def load(name):
    return pd.read_csv(DATA / name)

products = load("products.csv")
sources = load("sources.csv")
certs = load("certificates.csv")

st.title("Zenithi kataloogi assistent")
st.caption("Lihtne materjalivalik, mõõdud, artiklikoodid ja ametlikud allikad.")

query = st.text_input("Kirjuta kasutus või tingimus", placeholder="Näiteks: keemia, külm, sahk, lumi, õli, UV")

with st.sidebar:
    st.header("Filtrid")
    categories = st.multiselect("Materjalipere", sorted(products["kategooria"].unique()), default=sorted(products["kategooria"].unique()))
    statuses = st.multiselect("Kontrollistaatus", sorted(products["kontrollistaatus"].unique()), default=sorted(products["kontrollistaatus"].unique()))
    temp_min = st.slider("Min temp", int(products["min_temp_c"].min()), int(products["max_temp_c"].max()), int(products["min_temp_c"].min()))
    temp_max = st.slider("Max temp", int(products["min_temp_c"].min()), int(products["max_temp_c"].max()), int(products["max_temp_c"].max()))
    standard_only = st.checkbox("Ainult standard")
    only_custom = st.checkbox("Ainult erilahendused")
    only_pdf = st.checkbox("Ainult ametlik PDF olemas")

f = products.copy()
if query.strip():
    q = query.lower()
    mapping = {
        'keemia': ['chemical','oils','grease','solvents','acids'],
        'külm': ['-90','-40','-30'],
        'kuum': ['230','110','90'],
        'sahk': ['abrasion','wear','plow','snow'],
        'lumi': ['plow','snow','abrasion'],
        'õli': ['oil','oils','grease'],
        'uv': ['uv','ozone','weather'],
    }
    terms = []
    for k,v in mapping.items():
        if k in q:
            terms = v
            break
    if terms:
        mask = pd.Series(False, index=f.index)
        for col in ['toode','täisnimi','keemiline_vastupidavus','peamine_omadus','rakendus','märkused']:
            vals = f[col].astype(str).str.lower()
            for t in terms:
                mask = mask | vals.str.contains(t, na=False)
        f = f[mask]

f = f[f['kategooria'].isin(categories)]
f = f[f['kontrollistaatus'].isin(statuses)]
f = f[(f['min_temp_c'] >= temp_min) & (f['max_temp_c'] <= temp_max)]
if standard_only:
    f = f[f['standard_tase'].eq('standard')]
if only_custom:
    f = f[f['custom_available'].astype(str).str.lower().isin(['yes','true','1'])]
if only_pdf:
    f = f[f['pdf_url'].notna()]

st.subheader('Soovitused')
if f.empty:
    st.info('Tulemusi ei leitud. Proovi laiemaid filtreid.')
else:
    for _, r in f.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([2.2,1,1])
            with c1:
                st.markdown(f"**{r['toode']}** — {r['täisnimi']}")
                st.write(f"{r['standard_tase'].upper()} · {r['kontrollistaatus']}")
                st.write(f"{r['peamine_omadus']} | {r['rakendus']}")
            with c2:
                st.write(f"Artiklikood: `{r['artiklikood']}`")
                st.write(f"Kõvadus: {r['kõvadus_shore_a']}")
                st.write(f"Temp: {r['min_temp_c']}…{r['max_temp_c']} °C")
            with c3:
                st.write(f"Paksused: {r['standard_thicknesses_mm']}")
                st.write(f"Laius: {r['standard_widths_mm']} mm")
                st.write(f"Custom: {r['custom_available']}")
                if st.button('Näita allikaid', key=r['product_id']):
                    st.session_state['detail'] = r['product_id']

pid = st.session_state.get('detail')
if pid:
    st.divider()
    row = products[products['product_id'] == pid].iloc[0]
    st.subheader(f"Detailid: {row['toode']}")
    a,b = st.columns(2)
    with a:
        st.write({k: row[k] for k in ['kategooria','täisnimi','artiklikood','standard_tase','peamine_omadus','rakendus','märkused']})
        st.write('PDF:', row['pdf_url'])
        st.write('Tooteleht:', row['page_url'])
    with b:
        st.markdown('**Allikad**')
        st.dataframe(sources[sources['product_id']==pid], use_container_width=True, hide_index=True)
        st.markdown('**Sertifikaadid**')
        st.dataframe(certs[certs['product_id']==pid], use_container_width=True, hide_index=True)

st.caption('Spetsifikatsioonid võivad muutuda ilma etteteatamata. Kontrolli alati ametlikku allikat.')
