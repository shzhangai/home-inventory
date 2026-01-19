import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. PAGE CONFIG & APP TITLE (Must come first)
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE UNIFIED INITIALIZATION (The "Safe-Lock")
# We initialize EVERYTHING here before any other code runs.
if 'init_done' not in st.session_state:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        st.session_state.df = conn.read(ttl=0)
        st.session_state.needs_sync = False
        st.session_state.init_done = True
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        st.stop()

# 3. CALLBACKS (Logic handles local state only)
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state.needs_sync = True

def sync_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(data=st.session_state.df)
    st.session_state.needs_sync = False
    st.toast("✅ Cloud Updated!")

# 4. CSS (Forces single row and visible buttons)
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 45px !important;
    }
    button { height: 40px !important; width: 40px !important; padding: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# 5. MAIN UI
st.title("🍎 Pantry Pilot")

# Defensive check using .get() to prevent AttributeErrors
if st.session_state.get('needs_sync', False):
    st.button("☁️ SAVE TO GOOGLE SHEETS", on_click=sync_data, use_container_width=True, type="primary")

# Check if data exists in state
if 'df' in st.session_state and not st.session_state.df.empty:
    df = st.session_state.df
    
    # Selection logic
    all_locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", all_locs)
    
    cat_options = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cat_options, default=cat_options[0] if cat_options else None)

    st.divider()

    # 6. THE LIST
    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        c1, c2, c3 = st.columns([8, 1, 1])
        with c1:
            st.markdown(f"**{row['item_name']}** <span style='color:red; font-weight:bold;'>{int(row['item_quantity'])}</span>", unsafe_allow_html=True)
        with c2:
            st.button("＋", key=f"plus_{index}", on_click=update_qty, args=(index, 1))
        with c3:
            st.button("－", key=f"minus_{index}", on_click=update_qty, args=(index, -1))
        st.markdown("<hr style='margin:4px 0; opacity:0.1;'>", unsafe_allow_html=True)
else:
    st.warning("⚠️ No data loaded yet. Please check your Google Sheets connection.")
    if st.button("Retry Loading Data"):
        del st.session_state.init_done
        st.rerun()
