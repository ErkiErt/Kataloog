
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Zenithi assistent", layout="wide")
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

@st.cache_data

def load_csv(name):
    return pd.read_csv(DATA / name)

products = load_csv("products.csv")
sources = load_csv("sources.csv")
certs = load_csv("certificates.csv")

st.title("Zenithi kataloogi assistent")
st.caption("Leia sobiv materjal, mõõdud, tellimiskood ja erilahendused.")

query = st.text_input("Kirjuta kasutus või tingimus", placeholder="Näiteks: keemia, külm, sahk, lumi, õli")
col1, col2, col3 = st.columns(3)
with col1:
    standard_only = st.checkbox("Ainult standard")
with col2:
    show_premium = st.checkbox("Näita premium", value=True)
with col3:
    only_custom = st.checkbox("Näita erilahendused")

sidebar = st.sidebar
sidebar.header("Filtrid")
materials = sidebar.multiselect("Materjalipere", sorted(products["kategooria"].dropna().unique().tolist()), default=sorted(products["kategooria"].dropna().unique().tolist()))
status = sidebar.multiselect("Kontrollistaatus", sorted(products["kontrollistaatus"].dropna().unique().tolist()), default=sorted(products["kontrollistaatus"].dropna().unique().tolist()))
min_temp = sidebar.slider("Min temperatuur", int(products["min_temp_c"].min()), int(products["min_temp_c"].max()), int(products["min_temp_c"].min()))
max_temp = sidebar.slider("Max temperatuur", int(products["max_temp_c"].min()), int(products["max_temp_c"].max()), int(products["max_temp_c"].max()))
need_pdf = sidebar.checkbox("Ainult ametlik PDF olemas", value=False)
need_article = sidebar.checkbox("Ainult artiklikood olemas", value=False)
need_custom = sidebar.checkbox("Ainult erilahendused", value=False)

f = products.copy()
if query:
    q = query.lower()
    keywords = {
        "keemia": ["keemia", "chemical", "õlid", "kütus"],
        "külm": ["külm", "-90", "-40"],
        "kuum": ["kuumus", "230", "200", "120"],
        "sahk": ["sahk", "lumi", "plow", "abrasion"],
        "õli": ["õlid", "oil", "kütus"],
        "uv": ["uv", "osoon", "weather"],
    }
    matched = []
    for k, vals in keywords.items():
        if k in q:
            matched = vals
            break
    if matched:
        mask = False
        for term in matched:
            mask = mask | f[["toode","täisnimi","keemiline_vastupidavus","peamine_omadus","rakendus","märkused"]].astype(str).apply(lambda s: s.str.lower().str.contains(term, na=False)).any(axis=1)
        f = f[mask]

f = f[f["kategooria"].isin(materials)]
f = f[f["kontrollistaatus"].isin(status)]
f = f[(f["min_temp_c"] >= min_temp) & (f["max_temp_c"] <= max_temp)]
if standard_only:
    f = f[f["standard_tase"].eq("standard")]
if show_premium is False:
    f = f[f["standard_tase"].eq("standard")]
if only_custom:
    f = f[f["custom_available"].astype(str).str.lower().isin(["jah", "yes", "true", "1"])]
if need_pdf:
    f = f[f["artiklikood"].notna()]
if need_article:
    f = f[f["artiklikood"].notna() & (f["artiklikood"].astype(str).str.strip() != "")]

st.subheader("Soovitused")
if f.empty:
    st.info("Tulemusi ei leitud. Proovi laiemaid filtreid.")
else:
    for _, r in f.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                st.markdown(f"**{r['toode']}** · {r['täisnimi']}")
                st.write(f"Tase: {r['standard_tase']} · Kontroll: {r['kontrollistaatus']}")
                st.write(f"Milleks: {r['peamine_omadus']} · Kasutus: {r['rakendus']}")
            with c2:
                st.write(f"Artiklikood: {r['artiklikood']}")
                st.write(f"Mõõdud: {r['standard_thicknesses_mm']} mm")
                st.write(f"Laiused: {r['standard_widths_mm']} mm")
            with c3:
                st.write(f"Temp: {r['min_temp_c']}…{r['max_temp_c']} °C")
                st.write(f"Custom: {r['custom_available']}")
                if st.button(f"Detailid {r['product_id']}", key=r['product_id']):
                    st.session_state['detail'] = r['product_id']

pid = st.session_state.get('detail')
if pid:
    st.divider()
    row = products[products['product_id'] == pid].iloc[0]
    st.subheader(f"Detailid: {row['toode']}")
    a,b = st.columns(2)
    with a:
        st.write(row[['kategooria','täisnimi','artiklikood','peamine_omadus','rakendus','märkused']].to_dict())
    with b:
        src = sources[sources['product_id'] == pid]
        cf = certs[certs['product_id'] == pid]
        st.markdown("**Allikad**")
        st.dataframe(src, use_container_width=True, hide_index=True)
        st.markdown("**Sertifikaadid**")
        st.dataframe(cf, use_container_width=True, hide_index=True)

st.divider()
st.caption("Spetsifikatsioonid võivad muutuda ilma etteteatamata. Alati kontrolli ametlikku allikat.")
