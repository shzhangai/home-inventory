import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. Tighten the UI
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stElementContainer"] { margin-bottom: -10px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Data Connection
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 4. Main UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    g_locs = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    
    # Filter data for the view
    view_df = df[df['location'] == selected_loc].copy()
    
    # We only show specific columns to keep it tight
    display_df = view_df[['item_name', 'item_quantity', 'category']]

    # 5. THE DATA EDITOR (The Table)
    # This creates a perfect table where you can tap the quantity and change it
    edited_df = st.data_editor(
        display_df,
        column_config={
            "item_name": st.column_config.TextColumn("Item", width="large", disabled=True),
            "item_quantity": st.column_config.NumberColumn("Qty", width="small", min_value=0, step=1),
            "category": st.column_config.TextColumn("Cat", width="medium", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        key="pantry_editor"
    )

    # 6. Save Button (Since Data Editor handles multiple changes)
    if st.button("💾 Save Changes", use_container_width=True):
        # Merge the changes back to the original dataframe
        df.update(edited_df)
        conn.update(data=df)
        st.success("Inventory Updated!")
        st.rerun()

    st.divider()
    
    # Add Item Dialog remains the same
    @st.dialog("Add New Item")
    def add_item_dialog():
        new_name = st.text_input("Item Name")
        new_qty = st.number_input("Quantity", min_value=0, value=1)
        loc = st.selectbox("Location", g_locs)
        cat = st.selectbox("Category", sorted(df['category'].unique()))
        if st.button("Add"):
            new_row = {"item_name": new_name, "item_quantity": new_qty, "location": loc, "category": cat}
            updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated)
            st.rerun()

    if st.button("➕ Add New Item", use_container_width=True):
        add_item_dialog()

else:
    st.info("Pantry is empty!")
