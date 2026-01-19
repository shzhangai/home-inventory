import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# Custom CSS to make the buttons look better on mobile
st.markdown("""
    <style>
    /* Remove huge gaps between elements */
    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    /* Squeeze the main container padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    /* Make buttons shorter to save vertical space */
    div[data-testid="stButton"] > button {
        height: 30px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-top: -45px !important; /* This pulls the buttons UP into the name row */
    }
    </style>
""", unsafe_allow_html=True)

# 2. Connection & Data Loading
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 3. Add Item Dialog Function
@st.dialog("Add New Item")
def add_item_dialog(current_loc, current_cat, all_locs, global_cats):
    new_name = st.text_input("Item Name")
    new_qty = st.number_input("Quantity", min_value=0, value=1)
    
    # Location logic
    loc_choice = st.selectbox("Location", ["+ Add New Location"] + all_locs, 
                              index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New Location" else loc_choice
    
    # Category logic (Global)
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

# 4. Main App UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    # Get master lists
    global_locations = sorted(df['location'].dropna().unique().tolist())
    global_categories = sorted(df['category'].dropna().unique().tolist())
    
    # Selection UI
    selected_loc = st.selectbox("📍 View Location", global_locations)
    
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    
    default_cat = cats_in_loc[0] if cats_in_loc else ""
    selected_cat = st.pills("Category", cats_in_loc, default=default_cat)

    # Add Item Button
    if st.button("➕ Add New Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, global_locations, global_categories)

    st.divider()

# Items Display
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            # This creates a single line container for everything
            # We use flex-box to align them perfectly and remove gaps
            item_html = f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;">
                <div style="flex: 3; font-weight: bold; font-size: 16px;">{row['item_name']}</div>
                <div style="flex: 1; text-align: center; font-size: 18px; font-weight: bold; color: #555;">{int(row['item_quantity'])}</div>
                <div style="flex: 2; display: flex; justify-content: flex-end; gap: 5px;">
                    </div>
            </div>
            """
            st.markdown(item_html, unsafe_allow_html=True)
            
            # Since Streamlit buttons can't live inside raw HTML easily, 
            # we use columns ONLY for the buttons, but we make them tiny.
            # This 'floating' column trick places them over the 'empty' space we left above.
            btn_c1, btn_c2, btn_c3 = st.columns([6, 1.2, 1.2]) 
            with btn_c2:
                if st.button("🟢", key=f"add_{index}", use_container_width=True):
                    df.at[index, 'item_quantity'] += 1
                    df.at[index, 'last_add_date'] = datetime.now().strftime("%Y-%m-%d")
                    conn.update(data=df)
                    st.rerun()
            with btn_c3:
                if st.button("🔴", key=f"rem_{index}", use_container_width=True):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        df.at[index, 'last_remove_date'] = datetime.now().strftime("%Y-%m-%d")
                        conn.update(data=df)
                        st.rerun()

            # Note (if exists)
            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.caption(f"📝 {row['note']}")


else:
    # Everything below here must be indented by 4 spaces
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])    


