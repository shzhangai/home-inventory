import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 1. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Fetch Data (Refresh every 1 minute)
df = conn.read(ttl="1m")

st.title("🍎 Family Inventory")

if not df.empty:
    # 3. Filters
    all_locations = sorted(df['location'].dropna().unique())
    selected_loc = st.selectbox("📍 Location", all_locations)
    
    loc_df = df[df['location'] == selected_loc]
    
    all_cats = sorted(loc_df['category'].dropna().unique())
    selected_cat = st.pills("Category", all_cats, default=all_cats[0])

    st.divider()

    # 4. Final Filter
    final_df = loc_df[loc_df['category'] == selected_cat]

    for _, row in final_df.iterrows():
        # Layout: Item Name and Qty on top row
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {row['item_name']}")
        with col2:
            # Color the number red if it's out of stock
            color = "normal" if row['item_quantity'] > 0 else "inverse"
            st.metric("Qty", int(row['item_quantity']), delta_color=color)
        
        # Details in a "small print" section to save space
        expander_label = f"Details & Notes"
        if pd.notna(row['note']):
            expander_label += " 📝"
            
        with st.expander(expander_label):
            st.write(f"**Notes:** {row['note'] if pd.notna(row['note']) else 'None'}")
            st.caption(f"➕ Last Added: {row['last_add_date']}")
            st.caption(f"➖ Last Removed: {row['last_remove_date']}")
        
        st.divider()
else:
    st.info("Your pantry is empty! Add some items to the Google Sheet to begin.")
