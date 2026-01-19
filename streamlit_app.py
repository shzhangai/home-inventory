import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. Minimal CSS
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    /* Ensure the row looks like a clean list */
    .pantry-label { font-size: 16px; font-weight: 500; }
    .qty-label { font-size: 16px; font-weight: 900; color: #ff4b4b; margin-left: 8px; }
    hr { margin: 8px 0 !important; opacity: 0.1; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Instant Update Fragment
@st.fragment
def show_pantry_list(selected_loc, selected_cat):
    df = st.session_state.df
    items = df[(df['location'] == selected_loc) & (df['category'] == selected_cat)]
    
    for index, row in items.iterrows():
        # Using a 2-column layout where the right side is a joined button group
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown(f'<span class="pantry-label">{row["item_name"]}</span><span class="qty-label">{int(row["item_quantity"])}</span>', unsafe_allow_html=True)
        
        with col_right:
            # Segmented control acts as a "Toggle Button Group"
            # It's fast, visible, and stays on one line.
            action = st.segmented_control(
                label=f"actions_{index}",
                options=["MINUS", "PLUS"],
                selection_mode="single",
                key=f"ctrl_{index}",
                label_visibility="collapsed"
            )
            
            # Logic for the selection
            if action == "PLUS":
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun(scope="fragment")
            elif action == "MINUS":
                if row['item_quantity'] > 0:
                    st.session_state.df.at[index, 'item_quantity'] -= 1
                    conn.update(data=st.session_state.df)
                st.rerun(scope="fragment")
        
        st.markdown("<hr>", unsafe_allow_html=True)

# 5. UI Build
st.title("🍎 Pantry Pilot")

if not st.session_state.df.empty:
    locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    if st.button("➕ Add New Item", use_container_width=True, type="primary"):
        # Placeholder for your add logic
        st.info("Add logic goes here")

    st.divider()
    show_pantry_list(sel_loc, sel_cat)
