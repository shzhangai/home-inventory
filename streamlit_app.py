import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Tight, colorful, and no "boxes"
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force Row Behavior */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important;
    }

    /* Column 1 (Name + Qty) */
    [data-testid="column"]:nth-of-type(1) { flex: 10 !important; }
    
    /* Columns 2 & 3 (The Buttons) */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 40px !important; 
        min-width: 35px !important;
    }

    /* Target buttons in the list ONLY */
    [data-testid="stHorizontalBlock"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
        height: 40px !important;
        width: 40px !important;
    }

    /* Force the button text to be Green/Red and Big */
    [data-testid="column"]:nth-of-type(2) button p { color: #28a745 !important; font-size: 32px !important; font-weight: bold !important; }
    [data-testid="column"]:nth-of-type(3) button p { color: #dc3545 !important; font-size: 32px !important; font-weight: bold !important; }

    /* Remove hover background */
    [data-testid="stHorizontalBlock"] button:hover, 
    [data-testid="stHorizontalBlock"] button:active {
        background: transparent !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection and Session State
conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Fragment for INSTANT Updates
@st.fragment
def show_pantry_list(selected_loc, selected_cat):
    # Only work with the items in the selected category
    for index, row in st.session_state.df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            c1, c2, c3 = st.columns([10, 1, 1])
            
            with c1:
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 10px;">
                        <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 16px; font-weight: 800; color: #666;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                if st.button("+", key=f"add_{index}"):
                    st.session_state.df.at[index, 'item_quantity'] += 1
                    conn.update(data=st.session_state.df)
                    st.rerun()
            
            with c3:
                if st.button("-", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        st.session_state.df.at[index, 'item_quantity'] -= 1
                        conn.update(data=st.session_state.df)
                        st.rerun()

            st.markdown("<hr style='margin: 8px 0; opacity: 0.1;'>", unsafe_allow_html=True)

# 5. Main UI
st.title("🍎 Family Inventory")

df = st.session_state.df
if not df.empty:
    global_locations = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", global_locations)
    
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    selected_cat = st.pills("Category", cats_in_loc, default=cats_in_loc[0] if cats_in_loc else None)

    st.divider()
    
    # Call the fragment
    show_pantry_list(selected_loc, selected_cat)
