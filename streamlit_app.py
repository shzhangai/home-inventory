import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 1. ROBUST INITIALIZATION
conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

if 'needs_sync' not in st.session_state:
    st.session_state.needs_sync = False

# 2. CALLBACKS (Logic handled safely)
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state.needs_sync = True

def sync_data():
    conn.update(data=st.session_state.df)
    st.session_state.needs_sync = False
    st.toast("✅ Cloud Updated")

# 3. CSS for Mobile Density
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Ensure rows don't wrap */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* Column 1: Item Name & Qty */
    [data-testid="column"]:nth-of-type(1) { flex: 10 !important; }
    
    /* Column 2 & 3: Buttons */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 45px !important;
    }

    /* Solid Gray Buttons for reliability */
    button[kind="secondary"] {
        border-radius: 5px !important;
        height: 40px !important;
        width: 40px !important;
        font-weight: bold !important;
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Main UI
st.title("🍎 Pantry Pilot")

# Sync Button (Top of page)
if st.session_state.needs_sync:
    st.button("☁️ SYNC TO GOOGLE SHEETS", on_click=sync_data, use_container_width=True, type="primary")

df = st.session_state.df
if not df.empty:
    locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()

    # 5. THE LIST
    items_to_show = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items_to_show.iterrows():
        c1, c2, c3 = st.columns([10, 1, 1])
        
        with c1:
            # Name and Quantity on one line
            st.markdown(f"**{row['item_name']}** :red[{int(row['item_quantity'])}]")
            
        with c2:
            st.button("＋", key=f"p_{index}", on_click=update_qty, args=(index, 1))
            
        with c3:
            st.button("－", key=f"m_{index}", on_click=update_qty, args=(index, -1))
        
        st.markdown("<hr style='margin:0; opacity:0.1;'>", unsafe_allow_html=True)

else:
    st.info("No data found.")
