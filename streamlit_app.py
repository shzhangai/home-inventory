import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 1. THE SAFE INITIALIZATION (Must be at the very top)
if 'needs_sync' not in st.session_state:
    st.session_state['needs_sync'] = False

conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 2. CALLBACKS
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state['needs_sync'] = True

def sync_data():
    conn.update(data=st.session_state.df)
    st.session_state['needs_sync'] = False
    st.toast("✅ Cloud Updated")

# 3. CSS for Mobile Display
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force Row Behavior */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* Name Column takes most space */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    
    /* Button Columns stay small and fixed */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 42px !important; 
        min-width: 42px !important;
    }

    /* Simple, visible buttons */
    button {
        height: 38px !important;
        width: 38px !important;
        padding: 0px !important;
        border: 1px solid #ccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Main UI
st.title("🍎 Pantry Pilot")

# Sync Button
if st.session_state.get('needs_sync', False):
    st.button("☁️ SAVE TO GOOGLE", on_click=sync_data, use_container_width=True, type="primary")

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
        c1, c2, c3 = st.columns([8, 1, 1])
        
        with c1:
            # Item and Red quantity on one line
            st.markdown(f"**{row['item_name']}** <span style='color:red; font-weight:bold; margin-left:8px;'>{int(row['item_quantity'])}</span>", unsafe_allow_html=True)
            
        with c2:
            st.button("＋", key=f"p_{index}", on_click=update_qty, args=(index, 1))
            
        with c3:
            st.button("－", key=f"m_{index}", on_click=update_qty, args=(index, -1))
        
        st.markdown("<hr style='margin:4px 0; opacity:0.1;'>", unsafe_allow_html=True)

else:
    st.info("No data found.")
