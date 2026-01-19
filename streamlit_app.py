import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: The "Secret Sauce" for Mobile Layout
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* This creates a single row that CANNOT wrap or scroll */
    .pantry-item-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }

    /* Name and Qty stay together on the left */
    .item-main {
        display: flex;
        align-items: baseline;
        gap: 8px;
        flex: 1;
    }

    /* Buttons stay together on the right */
    .item-controls {
        display: flex;
        gap: 5px;
        align-items: center;
    }

    /* Strip all Streamlit styling from these specific buttons */
    .item-controls div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
        width: 45px !important;
        height: 45px !important;
        min-width: 45px !important;
    }

    /* Force the Color and Size of the text inside buttons */
    .plus-btn p { color: #28a745 !important; font-size: 35px !important; font-weight: 900 !important; }
    .minus-btn p { color: #dc3545 !important; font-size: 35px !important; font-weight: 900 !important; }

    /* Remove the gray hover circle */
    .item-controls button:hover, .item-controls button:active {
        background: transparent !important;
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
def show_pantry_items(selected_loc, selected_cat):
    # Filter locally for speed
    df = st.session_state.df
    items_to_show = df[(df['location'] == selected_loc) & (df['category'] == selected_cat)]
    
    for index, row in items_to_show.iterrows():
        # Open the Flexbox Row
        st.markdown(f"""
            <div class="pantry-item-row">
                <div class="item-main">
                    <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                    <span style="font-size: 17px; font-weight: 900; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                </div>
                <div class="item-controls">
        """, unsafe_allow_html=True)
        
        # Insert the actual Streamlit Buttons into the HTML Flexbox
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
            if st.button("+", key=f"add_{index}"):
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="minus-btn">', unsafe_allow_html=True)
            if st.button("-", key=f"rem_{index}"):
