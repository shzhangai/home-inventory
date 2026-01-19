import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Home Inventory", layout="centered")

# 1. INITIALIZE STATE
if "needs_sync" not in st.session_state:
    st.session_state["needs_sync"] = False

conn = st.connection("gsheets", type=GSheetsConnection)

if "df" not in st.session_state:
    try:
        st.session_state.df = conn.read(ttl=0)
    except Exception as e:
        st.error("Connection failed.")
        st.stop()

# 2. LOGIC
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state["needs_sync"] = True

def safe_sync():
    conn.update(data=st.session_state.df)
    st.session_state["needs_sync"] = False
    st.toast("✅ Saved!")

# 3. CSS - Minimal and Clean
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Style the buttons to be compact and square */
    div.stButton > button {
        width: 45px !important;
        height: 40px !important;
        padding: 0px !important;
        font-weight: bold !important;
    }
    
    /* Ensure the table takes full width but doesn't allow wrapping */
    .inventory-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .name-col { width: 60%; font-weight: bold; font-size: 15px; }
    .qty-col { width: 10%; color: red; font-weight: bold; text-align: center; font-size: 18px; }
    .btn-col { width: 15%; text-align: center; }
    
    hr { margin: 4px 0 !important; opacity: 0.2; }
    </style>
""", unsafe_allow_html=True)

# 4. UI TOP BAR
st.title("🏠 Home Inventory")

if st.session_state.get("needs_sync", False):
    st.button("💾 SAVE TO CLOUD", on_click=safe_sync, use_container_width=True, type="primary")

df = st.session_state.df
locs = sorted(df['location'].dropna().unique().tolist())
sel_loc = st.selectbox("📍 Location", locs)

cats = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

st.divider()

# 5. THE TABLE LIST
@st.fragment
def render_table_list(location, category):
    items = st.session_state.df[
        (st.session_state.df['location'] == location) & 
        (st.session_state.df['category'] == category)
    ]
    
    for index, row in items.iterrows():
        # We use a single set of columns, but we keep the buttons 
        # as close to the text as possible.
        col_main, col_p, col_m = st.columns([0.6, 0.2, 0.2])
        
        with col_main:
            # Item Name and Red Qty
            st.markdown(f"**{row['item_name']}** <span style='color:red; margin-left:10px;'>{int(row['item_quantity'])}</span>", unsafe_allow_html=True)
        
        with col_p:
            if st.button("＋", key=f"p_{index}"):
                update_qty(index, 1)
                st.rerun(scope="fragment")
        
        with col_m:
            if st.button("－", key=f"m_{index}"):
                update_qty(index, -1)
                st.rerun(scope="fragment")
        
        st.markdown("<hr>", unsafe_allow_html=True)

render_table_list(sel_loc, sel_cat)
