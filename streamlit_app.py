import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 1. KILL ALL GAPS WITH CSS
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* Style the links so they look like big, bold text signs */
    .pantry-btn {
        text-decoration: none !important;
        font-size: 24px !important;
        font-weight: bold !important;
        color: #007bff !important; /* Blue color so you know it's clickable */
        padding: 0 10px !important;
        display: inline-block;
    }
    .pantry-btn:active { color: #ff4b4b !important; }
    </style>
""", unsafe_allow_html=True)

# 2. DATA CONNECTION
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 3. CLICK DETECTION LOGIC
# This checks if a + or - was clicked in the URL
params = st.query_params
if "action" in params and "id" in params:
    idx = int(params["id"])
    action = params["action"]
    
    if action == "add":
        df.at[idx, 'item_quantity'] += 1
    elif action == "rem" and df.at[idx, 'item_quantity'] > 0:
        df.at[idx, 'item_quantity'] -= 1
        
    conn.update(data=df)
    st.query_params.clear() # Reset the URL
    st.rerun()

st.title("🍎 Pantry")

if df is not None and not df.empty:
    # Basic filters
    g_locs = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    loc_df = df[df['location'] == selected_loc]

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. THE ROW DISPLAY (HTML ONLY)
    for index, row in loc_df.iterrows():
        # We build one single HTML line for Name, Qty, +, and -
        # This ensures they are literally right next to each other
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-start; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                <div style="flex-grow: 1; font-size: 15px;">
                    <b>{row['item_name']}</b> 
                    <span style="color: #ff4b4b; margin-left: 10px; font-weight: 800;">{int(row['item_quantity'])}</span>
                </div>
                <div style="display: flex; gap: 20px;">
                    <a href="/?action=add&id={index}" target="_self" class="pantry-btn">+</a>
                    <a href="/?action=rem&id={index}" target="_self" class="pantry-btn">−</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
