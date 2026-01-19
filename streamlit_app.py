import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 1. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Fetch Data
# We use st.cache_data to keep it snappy, but clear it when we save
df = conn.read(ttl=0)

st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    # --- FILTERS ---
    all_locations = sorted(df['location'].dropna().unique())
    selected_loc = st.selectbox("📍 Location", all_locations)
    
    loc_df = df[df['location'] == selected_loc]
    all_cats = sorted(loc_df['category'].dropna().unique())
    selected_cat = st.pills("Category", all_cats, default=all_cats[0])

    st.divider()

    # --- ITEMS LIST ---
    # We loop through the ORIGINAL dataframe so we can update it by index
    for index, row in df.iterrows():
        # Only show items matching the filters
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{row['item_name']}**")
                st.caption(f"Qty: {int(row['item_quantity'])}")
            
            # Plus / Minus Buttons
            with col2:
                if st.button("➕", key=f"add_{index}"):
                    df.at[index, 'item_quantity'] += 1
                    df.at[index, 'last_add_date'] = datetime.now().strftime("%Y-%m-%d")
                    conn.update(data=df)
                    st.rerun()

            with col3:
                if st.button("➖", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        df.at[index, 'last_remove_date'] = datetime.now().strftime("%Y-%m-%d")
                        conn.update(data=df)
                        st.rerun()
            
            st.divider()

else:
    st.warning("Your Google Sheet looks empty!")
