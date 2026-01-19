import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: High Contrast for S24+
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

    /* Column Widths */
    [data-testid="column"]:nth-of-type(1) { flex: 10 !important; }
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 40px !important;
    }

    /* THE BUTTON FIX: Light gray circles so they are ALWAYS visible */
    [data-testid="stHorizontalBlock"] button {
        border: 1px solid #eeeeee !important;
        background-color: #f0f2f6 !important; /* Light gray background */
        border-radius: 50% !important; /* Circular buttons */
        height: 38px !important;
        width: 38px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0px !important;
    }

    /* Force the actual symbol (+) to be Green */
    [data-testid="column"]:nth-of-type(2) button p { 
        color: #28a745 !important; 
        font-size: 24px !important; 
        font-weight: 900 !important; 
    }
    
    /* Force the actual symbol (-) to be Red */
    [data-testid="column"]:nth-of-type(3) button p { 
        color: #dc3545 !important; 
        font-size: 24px !important; 
        font-weight: 900 !important; 
    }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection and Session State
conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Instant Update Fragment
@st.fragment
def show_pantry_list(selected_loc, selected_cat):
    df_local = st.session_state.df
    for index, row in df_local.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            c1, c2, c3 = st.columns([10, 1, 1])
            
            with c1:
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 10px;">
                        <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 16px; font-weight: 800; color: #ff4b4b;">{int(row['item_quantity'])}</span>
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

# 5. UI Build
st.title("🍎 Family Inventory")

if not st.session_state.df.empty:
    global_locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", global_locs)
    
    cat_df = st.session_state.df[st.session_state.df['location'] == sel_loc]
    cats = sorted(cat_df['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()
    show_pantry_list(sel_loc, sel_cat)
