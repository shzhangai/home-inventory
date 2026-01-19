# --- THE "ADD NEW ITEM" DIALOG FUNCTION ---
# 1. IMPORTS FIRST
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 2. PAGE CONFIG SECOND
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 3. CONNECTION THIRD
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 4. FUNCTIONS (The Dialog) FOURTH
@st.dialog("Add New Item")
def add_item_dialog(current_loc, current_cat, all_locs, global_cats):
 
    # Form Fields
    new_name = st.text_input("Item Name")
    new_qty = st.number_input("Quantity", min_value=0, value=1)
    
    # Location logic: Select existing or type new
    loc_choice = st.selectbox("Location", ["+ Add New Location"] + all_locs, 
                              index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New Location" else loc_choice
    
    # Category logic: NOW SHOWS ALL CATEGORIES FROM THE ENTIRE SHEET
    cat_choice = st.selectbox("Category", ["+ Add New Category"] + global_cats, 
                              index=global_cats.index(current_cat)+1 if current_cat in global_cats else 0)
    final_cat = st.text_input("New Category Name") if cat_choice == "+ Add New Category" else cat_choice
    
    new_note = st.text_area("Note (Optional)")

    if st.button("Save to Inventory"):
        if new_name and final_loc and final_cat:
            new_row = {
                "category": final_cat,
                "item_name": new_name,
                "item_quantity": new_qty,
                "location": final_loc,
                "last_add_date": datetime.now().strftime("%Y-%m-%d"),
                "last_remove_date": "",
                "note": new_note
            }
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Added!")
            st.rerun()
        else:
            st.error("Please fill in Name, Location, and Category.")

# --- MAIN APP UI ---
st.title("🍎 Family Inventory")

if df is not None:
    # Get GLOBAL lists for the Add Item dialog
    global_locations = sorted(df['location'].dropna().unique().tolist())
    global_categories = sorted(df['category'].dropna().unique().tolist())
    
    # FILTERS for the current view
    selected_loc = st.selectbox("📍 View Location", global_locations)
    
    loc_df = df[df['location'] == selected_loc]
    # Categories specific to the selected location (for the pill buttons)
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    
    default_cat = cats_in_loc[0] if cats_in_loc else ""
    selected_cat = st.pills("Category", cats_in_loc, default=default_cat)

    # PASS global_categories to the dialog
    if st.button("➕ Add New Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, global_locations, global_categories)
