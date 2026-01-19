import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry", layout="centered")

# 2. Minimal CSS to tighten the display
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    /* Standard link styling so they don't look like blue URLs */
    a { text-decoration: none !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection & Session State
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Action Handler (Calculates change before the fragment renders)
params = st.query_params
if "action" in params and "id" in params:
    idx = int(params["id"])
    if params["action"] == "add":
        st.session_state.df.at[idx, 'item_quantity'] += 1
    elif params["action"] == "rem" and st.session_state.df.at[idx, 'item_quantity'] > 0:
        st.session_state.df.at[idx, 'item_quantity'] -= 1
    
    # Save and Refresh
    conn.update(data=st.session_state.df)
    st.query_params.clear()
    st.rerun()

# 5. UI Build
st.title("🍎 Pantry Pilot")

df = st.session_state.df
if not df.empty:
    # Navigation
    locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()

    # 6. The Single-Row List
    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        qty = int(row['item_quantity'])
        
        # We use a single Markdown line with HTML for the layout.
        # 🟢 = Plus, 🔴 = Minus. These will ALWAYS be visible.
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee;">
                <div style="flex-grow: 1;">
                    <span style="font-size: 16px;">{row['item_name']}</span>
                    <span style="font-size: 16px; font-weight: bold; color: #ff4b4b; margin-left: 10px;">{qty}</span>
                </div>
                <div style="display: flex; gap: 25px; padding-right: 10px;">
                    <a href="/?action=add&id={index}" target="_self" style="font-size: 24px;">🟢</a>
                    <a href="/?action=rem&id={index}" target="_self" style="font-size: 24px;">🔴</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if st.button("➕ Add New Item", use_container_width=True):
        st.info("Dialog logic here")

else:
    st.info("Pantry is empty.")
