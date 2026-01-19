import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Home Inventory", layout="centered")

# 1. INITIALIZE STATE (Linear & Safe)
if "needs_sync" not in st.session_state:
    st.session_state["needs_sync"] = False

conn = st.connection("gsheets", type=GSheetsConnection)

if "df" not in st.session_state:
    try:
        st.session_state.df = conn.read(ttl=0)
    except Exception as e:
        st.error("Connection failed.")
        st.stop()

# 2. LOGIC FUNCTIONS
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state["needs_sync"] = True

def safe_sync():
    conn.update(data=st.session_state.df)
    st.session_state["needs_sync"] = False
    st.toast("✅ Saved!")

# 3. CSS (The "No-Scroll" Lock)
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stHorizontalBlock"] { 
        display: flex !important; 
        flex-wrap: nowrap !important; 
    }
    div.stButton > button {
        width: 100% !important;
        height: 40px !important;
        padding: 0 !important;
    }
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

# 5. THE INSTANT FRAGMENT
# This only reruns the list below, making taps feel instant.
@st.fragment
def render_inventory_list(location, category):
    # Filter local state
    items = st.session_state.df[
        (st.session_state.df['location'] == location) & 
        (st.session_state.df['category'] == category)
    ]
    
    for index, row in items.iterrows():
        # Using fixed small ratios to force buttons onto the screen
        c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
        
        with c1:
            st.markdown(f"**{row['item_name']}** <span style='color:red; font-weight:bold;'>{int(row['item_quantity'])}</span>", unsafe_allow_html=True)
        
        with c2:
            # We use st.rerun(scope="fragment") for instant UI feedback
            if st.button("＋", key=f"p_{index}"):
                update_qty(index, 1)
                st.rerun(scope="fragment")
                
        with c3:
            if st.button("－", key=f"m_{index}"):
                update_qty(index, -1)
                st.rerun(scope="fragment")
        
        st.markdown("<hr style='margin:2px 0; opacity:0.1;'>", unsafe_allow_html=True)

# Run the fragment
render_inventory_list(sel_loc, sel_cat)
