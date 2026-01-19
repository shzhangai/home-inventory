import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 1. Connection & Session State Initialization
conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)
    st.session_state.needs_sync = False

# 2. Update Functions (Logic separated from UI)
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state.needs_sync = True

def sync_data():
    conn.update(data=st.session_state.df)
    st.session_state.needs_sync = False
    st.toast("✅ Changes saved to Google Sheets")

# 3. CSS for tight mobile layout
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    .item-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
    .item-name { font-size: 16px; flex-grow: 1; }
    .item-qty { font-size: 18px; font-weight: bold; color: #ff4b4b; margin: 0 15px; min-width: 25px; text-align: center; }
    /* Style buttons to be small circles */
    div.stButton > button {
        border-radius: 50% !important;
        width: 35px !important;
        height: 35px !important;
        padding: 0px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Main UI
st.title("🍎 Pantry Pilot")

# Show Sync button if changes exist
if st.session_state.needs_sync:
    st.button("💾 SAVE TO GOOGLE SHEETS", on_click=sync_data, use_container_width=True, type="primary")

if not st.session_state.df.empty:
    df = st.session_state.df
    locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()

    # 5. The List using simple Columns (No segmented control to avoid KeyError)
    items_to_show = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items_to_show.iterrows():
        # We use a container to keep everything tight
        with st.container():
            col1, col2, col3, col4 = st.columns([6, 1, 2, 1])
            
            with col1:
                st.markdown(f"**{row['item_name']}**")
            
            with col2:
                # Minus button
                st.button("−", key=f"min_{index}", on_click=update_qty, args=(index, -1))
                
            with col3:
                # Quantity display
                st.markdown(f"<div style='text-align:center; color:#ff4b4b; font-weight:bold; font-size:18px;'>{int(row['item_quantity'])}</div>", unsafe_allow_html=True)
                
            with col4:
                # Plus button
                st.button("＋", key=f"pls_{index}", on_click=update_qty, args=(index, 1))
            
            st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
else:
    st.info("No items found.")
