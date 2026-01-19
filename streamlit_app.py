import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry", layout="centered")

# 2. THE CSS: This forces the columns to stay small and keeps buttons as solid circles
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force columns into a single row that NEVER wraps */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* Name Column */
    [data-testid="column"]:nth-of-type(1) { flex: 10 !important; }
    
    /* Button Columns: Small and fixed */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 45px !important;
    }

    /* Style the buttons as solid circles so they can't be invisible */
    [data-testid="stHorizontalBlock"] button {
        height: 38px !important;
        width: 38px !important;
        border-radius: 50% !important;
        border: none !important;
        padding: 0px !important;
    }

    /* Green Plus Button */
    [data-testid="column"]:nth-of-type(2) button { background-color: #28a745 !important; }
    [data-testid="column"]:nth-of-type(2) button p { color: white !important; font-size: 22px !important; font-weight: bold !important; }

    /* Red Minus Button */
    [data-testid="column"]:nth-of-type(3) button { background-color: #dc3545 !important; }
    [data-testid="column"]:nth-of-type(3) button p { color: white !important; font-size: 22px !important; font-weight: bold !important; }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Data Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Instant Update Fragment (No page reload)
@st.fragment
def show_pantry_items(sel_loc, sel_cat):
    df = st.session_state.df
    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        # Columns stay on one line because of the CSS above
        c1, c2, c3 = st.columns([10, 1, 1])
        
        with c1:
            st.markdown(f"""
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="font-size: 15px;">{row['item_name']}</span>
                    <span style="font-size: 15px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            if st.button("＋", key=f"add_{index}"):
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun(scope="fragment") # Updates only the list instantly
                
        with c3:
            if st.button("－", key=f"rem_{index}"):
                if row['item_quantity'] > 0:
                    st.session_state.df.at[index, 'item_quantity'] -= 1
                    conn.update(data=st.session_state.df)
                    st.rerun(scope="fragment")
        
        st.markdown("<hr style='margin: 4px 0; opacity: 0.1;'>", unsafe_allow_html=True)

# 5. UI Build
st.title("🍎 Pantry Pilot")

if not st.session_state.df.empty:
    locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cat_df = st.session_state.df[st.session_state.df['location'] == sel_loc]
    cats = sorted(cat_df['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()
    show_pantry_items(sel_loc, sel_cat)
