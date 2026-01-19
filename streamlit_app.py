import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# --- CSS: Target the specific button containers to remove the white boxes ---
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force columns to stay together */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important;
    }

    /* Style the buttons to look like plain text, no boxes */
    div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: #31333F !important;
        font-size: 24px !important;
        font-weight: bold !important;
        height: 30px !important;
        width: 30px !important;
        padding: 0px !important;
        margin: 0px !important;
        line-height: 1 !important;
    }

    /* Remove the 'hover' white background effect */
    div[data-testid="stButton"] > button:hover {
        background: transparent !important;
        color: #ff4b4b !important;
    }

    /* Column widths: Item name is 80%, buttons are tiny */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { flex: 1 !important; max-width: 40px !important; }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- UI Header ---
st.title("🍎 Pantry")

if df is not None and not df.empty:
    g_locs = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    selected_cat = st.pills("Category", cats_in_loc, default=cats_in_loc[0] if cats_in_loc else None)

    # Simplified Add Button
    if st.button("➕ New Item", use_container_width=True):
        st.info("Dialog function would trigger here")

    st.markdown("---")

    # --- THE LIST ---
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            c1, c2, c3 = st.columns([8, 1, 1])
            
            with c1:
                # Name and Qty right next to each other
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 14px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 14px; font-weight: 800; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                # The 'plus' as a clean text-button
                if st.button("+", key=f"add_{index}"):
                    df.at[index, 'item_quantity'] += 1
                    conn.update(data=df)
                    st.rerun()
            
            with c3:
                # The 'minus' as a clean text-button
                if st.button("-", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun()

            st.markdown("<hr style='margin: 0px; opacity: 0.1;'>", unsafe_allow_html=True)
