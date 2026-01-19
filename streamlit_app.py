import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Tight alignment and specific colors for the text signs
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Container for the whole row */
    .pantry-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #eee;
    }

    /* Left side: Name and Qty */
    .item-info {
        display: flex;
        align-items: baseline;
        gap: 10px;
        flex-grow: 1;
    }

    /* Right side: The +/- signs */
    .controls {
        display: flex;
        gap: 20px; /* Space between plus and minus */
        padding-right: 10px;
    }

    /* Style the signs to look like bold text, not buttons */
    .sign-link {
        text-decoration: none !important;
        font-size: 32px !important;
        font-weight: bold !important;
        line-height: 1;
    }
    
    .plus { color: #28a745 !important; }
    .minus { color: #dc3545 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Data Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = conn.read(ttl=0)

# 4. Action Handler
params = st.query_params
if "action" in params and "id" in params:
    idx = int(params["id"])
    if params["action"] == "add":
        st.session_state.inventory_df.at[idx, 'item_quantity'] += 1
    elif params["action"] == "rem" and st.session_state.inventory_df.at[idx, 'item_quantity'] > 0:
        st.session_state.inventory_df.at[idx, 'item_quantity'] -= 1
    
    # Background update to Google Sheets
    conn.update(data=st.session_state.inventory_df)
    st.query_params.clear()
    st.rerun()

# 5. Main UI
st.title("🍎 Family Inventory")

df = st.session_state.inventory_df
if not df.empty:
    g_locs = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    selected_cat = st.pills("Category", cats_in_loc, default=cats_in_loc[0] if cats_in_loc else None)

    st.divider()

    # 6. The List (Using HTML for perfect spacing)
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            st.markdown(f"""
                <div class="pantry-row">
                    <div class="item-info">
                        <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 16px; font-weight: 800; color: #666;">{int(row['item_quantity'])}</span>
                    </div>
                    <div class="controls">
                        <a href="/?action=add&id={index}" target="_self" class="sign-link plus">+</a>
                        <a href="/?action=rem&id={index}" target="_self" class="sign-link minus">−</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -8px; margin-bottom: 8px;'>📝 {row['note']}</div>", unsafe_allow_html=True)

# 7. Add Button (placed at the bottom for better mobile reach)
st.write("")
if st.button("➕ Add New Item", use_container_width=True):
    st.info("Trigger add dialog")
