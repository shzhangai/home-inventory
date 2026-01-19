import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: High visibility and tight row control
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .pantry-item-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }

    .item-main {
        display: flex;
        align-items: baseline;
        gap: 8px;
        flex: 1;
    }

    /* Style the buttons to be invisible boxes with colored text */
    div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
        width: 45px !important;
        height: 45px !important;
    }

    /* Colors and sizes for the symbols */
    .plus-btn p { color: #28a745 !important; font-size: 32px !important; font-weight: 900 !important; }
    .minus-btn p { color: #dc3545 !important; font-size: 32px !important; font-weight: 900 !important; }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection and Session State
conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Instant Update Fragment (Fixed Indentation)
@st.fragment
def show_pantry_items(selected_loc, selected_cat):
    df = st.session_state.df
    # Filter items
    items_to_show = df[(df['location'] == selected_loc) & (df['category'] == selected_cat)]
    
    for index, row in items_to_show.iterrows():
        # Layout container
        st.markdown(f"""
            <div class="pantry-item-row">
                <div class="item-main">
                    <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                    <span style="font-size: 17px; font-weight: 900; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Buttons in their own small column row to prevent stacking
        bt1, bt2 = st.columns([1, 1])
        with bt1:
            st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
            if st.button("+", key=f"add_{index}"):
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun(scope="fragment")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with bt2:
            st.markdown('<div class="minus-btn">', unsafe_allow_html=True)
            if st.button("-", key=f"rem_{index}"):
                if row['item_quantity'] > 0:
                    st.session_state.df.at[index, 'item_quantity'] -= 1
                    conn.update(data=st.session_state.df)
                    st.rerun(scope="fragment")
            st.markdown('</div>', unsafe_allow_html=True)

# 5. Main UI
st.title("🍎 Family Inventory")

if not st.session_state.df.empty:
    g_locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", g_locs)
    
    cat_df = st.session_state.df[st.session_state.df['location'] == sel_loc]
    cats = sorted(cat_df['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()
    
    # Run fragment
    show_pantry_items(sel_loc, sel_cat)
else:
    st.info("No items found. Add one to get started!")
