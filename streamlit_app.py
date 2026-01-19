import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry", layout="centered")

# 1. CSS: Forcing the button to look like a simple flat row
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Make buttons full width but very short and flat */
    div.stButton > button {
        width: 100% !important;
        border: 1px solid #eee !important;
        background-color: white !important;
        padding: 5px 10px !important;
        height: auto !important;
        text-align: left !important;
    }
    
    /* Ensure the text inside the button is spread out */
    div.stButton p {
        width: 100% !important;
        display: flex !important;
        justify-content: space-between !important;
        font-size: 16px !important;
        margin: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 2. THE UI
st.title("🍎 Pantry Pilot")

df = st.session_state.df
if not df.empty:
    locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()

    # 3. THE LIST: Every row is a pair of buttons
    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        qty = int(row['item_quantity'])
        
        # We put both actions into simple, full-width rows.
        # This is impossible to "stack" because it's already a full row.
        # Button 1: Name, Quantity, and the PLUS sign
        if st.button(f"{row['item_name']}       {qty}       ＋", key=f"add_{index}"):
            st.session_state.df.at[index, 'item_quantity'] += 1
            conn.update(data=st.session_state.df)
            st.rerun()
            
        # Button 2: A small "Minus" row right under the main one
        if st.button(f"
