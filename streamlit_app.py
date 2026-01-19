import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data
df = conn.read(ttl=0)

st.title("🍎 Family Inventory")

# SAFETY CHECK: If the sheet is empty or columns are wrong
if df is not None and not df.empty:
    try:
        all_locations = sorted(df['location'].dropna().unique())
        
        if all_locations:
            selected_loc = st.selectbox("📍 Location", all_locations)
            loc_df = df[df['location'] == selected_loc]
            
            all_cats = sorted(loc_df['category'].dropna().unique())
            
            if all_cats:
                selected_cat = st.pills("Category", all_cats, default=all_cats[0])
                st.divider()

                final_df = loc_df[loc_df['category'] == selected_cat]
                for _, row in final_df.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {row['item_name']}")
                        st.caption(f"Last Added: {row['last_add_date']}")
                    with col2:
                        st.metric("Qty", int(row['item_quantity']))
                    st.divider()
            else:
                st.info("Add a 'category' to your items in this location!")
        else:
            st.info("Your 'location' column seems empty. Add a location to your items!")
            
    except KeyError as e:
        st.error(f"Missing column in Google Sheet: {e}")
else:
    st.warning("Wait! Your Google Sheet looks empty. Add one item to see it here.")
