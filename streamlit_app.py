import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pantry Pilot", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- THE "ADD NEW ITEM" DIALOG FUNCTION ---
@st.dialog("Add New Item")
def add_item_dialog(current_loc, current_cat, all_locs, all_cats):
    # Form Fields
    new_name = st.text_input("Item Name")
    new_qty = st.number_input("Quantity", min_value=0, value=1)
    
    # Location logic: Select existing or type new
    loc_choice = st.selectbox("Location", ["+ Add New Location"] + all_locs, index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New Location" else loc_choice
    
    # Category logic: Select existing or type new
    cat_choice = st.selectbox("Category", ["+ Add New Category"] + all_cats, index=all_cats.index(current_cat)+1 if current_cat in all_cats else 0)
    final_cat = st.text_input("New Category Name") if cat_choice == "+ Add New Category" else cat_choice
    
    new_note = st.text_area("Note (Optional)")

    if st.button("Save to Inventory"):
        if new_name and final_loc and final_cat:
            # Create a new row
            new_row = {
                "category": final_cat,
                "item_name": new_name,
                "item_quantity": new_qty,
                "location": final_loc,
                "last_add_date": datetime.now().strftime("%Y-%m-%d"),
                "last_remove_date": "",
                "note": new_note
            }
            # Append and Update
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Added!")
            st.rerun()
        else:
            st.error("Please fill in Name, Location, and Category.")

# --- MAIN APP UI ---
st.title("🍎 Family Inventory")

if df is not None:
    # FILTERS
    all_locations = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", all_locations)
    
    loc_df = df[df['location'] == selected_loc]
    all_cats = sorted(loc_df['category'].dropna().unique().tolist())
    
    # If no categories exist yet for a new location
    default_cat = all_cats[0] if all_cats else ""
    selected_cat = st.pills("Category", all_cats, default=default_cat)

    # ADD BUTTON (Floating at the top of the list)
    if st.button("➕ Add New Item to this Section", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, all_locations, all_cats)

    st.divider()

    # ITEMS LIST
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            col1, col2, col3 = st.columns([2, 0.5, 0.5])
            with col1:
                st.markdown(f"**{row['item_name']}**")
                st.caption(f"Qty: {int(row['item_quantity'])}")
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
