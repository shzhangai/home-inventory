import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Direct styling for the HTML links
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .pantry-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }

    .item-info {
        display: flex;
        align-items: baseline;
        gap: 10px;
        flex-grow: 1;
    }

    .controls {
        display: flex;
        gap: 20px;
        align-items: center;
    }

    /* Standard HTML Link styling - much more reliable than st.button CSS */
    .btn-link {
        text-decoration: none !important;
        font-size: 32px !important;
        font-weight: 900 !important;
        line-height: 1;
        padding: 5px 10px;
    }
    
    .plus { color: #28a745 !important; }
    .minus { color: #dc3545 !important; }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection & Data Handling
conn = st.connection("gsheets", type=GSheetsConnection)

# Keep data in session state for speed
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Action Handler (This runs before the UI renders)
params = st.query_params
if "action" in params and "id" in params:
    idx = int(params["id"])
    if params["action"] == "add":
        st.session_state.df.at[idx, 'item_quantity'] += 1
    elif params["action"] == "rem" and st.session_state.df.at[idx, 'item_quantity'] > 0:
        st.session_state.df.at[idx, 'item_quantity'] -= 1
    
    # Update Google Sheets in the background
    conn.update(data=st.session_state.df)
    # Clear params and rerun to show the change immediately
    st.query_params.clear()
    st.rerun()

# 5. UI Build
st.title("🍎 Pantry")

df = st.session_state.df
if not df.empty:
    locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cat_df = df[df['location'] == sel_loc]
    cats = sorted(cat_df['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()

    # 6. The List using pure HTML for the row
    for index, row in df.iterrows():
        if row['location'] == sel_loc and row['category'] == sel_cat:
            st.markdown(f"""
                <div class="pantry-row">
                    <div class="item-info">
                        <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 17px; font-weight: 900; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                    </div>
                    <div class="controls">
                        <a href="/?action=add&id={index}" target="_self" class="btn-link plus">+</a>
                        <a href="/?action=rem&id={index}" target="_self" class="btn-link minus">−</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.info("No items found.")
