import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry", layout="centered")

# 2. Minimal CSS to remove extra padding
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection & Session State
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Main UI
st.title("🍎 Pantry Pilot")

df = st.session_state.df

if not df.empty:
    # Filter Controls
    locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cat_df = df[df['location'] == sel_loc]
    cats = sorted(cat_df['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    # Filter the data for display
    display_df = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)].copy()
    
    # We add a "Change" column to handle the +/- logic without big spaces
    display_df = display_df[['item_name', 'item_quantity']]

    # 5. THE DATA EDITOR: This is the most stable layout for mobile
    # It allows you to tap the number and type, OR use the tiny +/- arrows
    edited_df = st.data_editor(
        display_df,
        column_config={
            "item_name": st.column_config.TextColumn("Item", width="large", disabled=True),
            "item_quantity": st.column_config.NumberColumn(
                "Qty",
                help="Tap to change",
                min_value=0,
                step=1,
                format="%d",
                width="small"
            ),
        },
        hide_index=True,
        use_container_width=True,
        key="pantry_editor"
    )

    # 6. Save Logic
    if st.button("💾 Sync Changes", use_container_width=True, type="primary"):
        # Merge edited values back to the main session state
        for idx, row in edited_df.iterrows():
            item_name = row['item_name']
            new_qty = row['item_quantity']
            st.session_state.df.loc[st.session_state.df['item_name'] == item_name, 'item_quantity'] = new_qty
        
        conn.update(data=st.session_state.df)
        st.success("Saved!")
        st.rerun()

else:
    st.info("Pantry is empty.")
