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

# 3. CSS (Making buttons wide and touch-friendly for mobile)
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Make buttons wide enough for easy tapping but keep them side-by-side */
    div.stButton > button {
        width: 80px !important;
        height: 45px !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    .item-header { font-size: 18px; margin-bottom: -10px; }
    .qty-text { color: red; font-weight: bold; font-size: 20px; }
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

# 5. THE INSTANT LIST
@st.fragment
def render_list(location, category):
    items = st.session_state.df[
        (st.session_state.df['location'] == location) & 
        (st.session_state.df['category'] == category)
    ]
    
    for index, row in items.iterrows():
        # Display name and quantity on top
        st.markdown(f"**{row['item_name']}** : <span class='qty-text'>{int(row['item_quantity'])}</span>", unsafe_allow_html=True)
        
        # Put buttons in a small row immediately underneath
        # This prevents the "pushing to the right" effect entirely
        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
        
        with btn_col1:
            if st.button("＋", key=f"p_{index}"):
                update_qty(index, 1)
                st.rerun(scope="fragment")
        with btn_col2:
            if st.button("－", key=f"m_{index}"):
                update_qty(index, -1)
                st.rerun(scope="fragment")
        
        st.markdown("<hr style='margin:8px 0; opacity:0.1;'>", unsafe_allow_html=True)

render_list(sel_loc, sel_cat)
