import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Focus on stopping the "Stacking" behavior
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force columns to NOT stack on mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* Column 1: Item Name (Flexible) */
    [data-testid="column"]:nth-of-type(1) {
        flex: 10 !important;
        min-width: 0px !important;
    }
    
    /* Columns 2 & 3: Buttons (Fixed small width) */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) {
        flex: 1 !important;
        max-width: 45px !important;
        min-width: 45px !important;
    }

    /* Button styling: No background, just bold colored text */
    div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
        height: 40px !important;
        width: 40px !important;
    }

    /* Plus color */
    [data-testid="column"]:nth-of-type(2) button p {
        color: #28a745 !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }

    /* Minus color */
    [data-testid="column"]:nth-of-type(3) button p {
        color: #dc3545 !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Update Fragment
@st.fragment
def show_pantry_list(selected_loc, selected_cat):
    df = st.session_state.df
    items = df[(df['location'] == selected_loc) & (df['category'] == selected_cat)]
    
    for index, row in items.iterrows():
        # Create 3 columns that the CSS above will force to stay in one row
        cols = st.columns([10, 1, 1])
        
        with cols[0]:
            # Standard HTML for the red quantity to ensure it works
            st.markdown(f"""
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                    <span style="font-size: 16px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with cols[1]:
            if st.button("+", key=f"add_{index}"):
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun(scope="fragment")
                
        with cols[2]:
            if st.button("-", key=f"rem_{index}"):
                if row['item_quantity'] > 0:
                    st.session_state.df.at[index, 'item_quantity'] -= 1
                    conn.update(data=st.session_state.df)
                    st.rerun(scope="fragment")
        
        st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)

# 5. UI Build
st.title("🍎 Pantry")

if not st.session_state.df.empty:
    locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    current_cats = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", current_cats, default=current_cats[0] if current_cats else None)

    st.divider()
    show_pantry_list(sel_loc, sel_cat)
