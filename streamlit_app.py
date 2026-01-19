import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# Custom CSS for a tight mobile UI
st.markdown("""
    <style>
    /* Force the main container to be wide */
    .block-container { padding: 1rem 0.5rem !important; }

    /* Remove the vertical gap between the HTML name and the Button columns */
    [data-testid="stVerticalBlock"] > div {
        margin-top: -5px !important;
        margin-bottom: -5px !important;
    }

    /* Style the buttons to be very small circles */
    div[data-testid="stButton"] > button {
        height: 30px !important;
        width: 30px !important;
        min-width: 30px !important;
        padding: 0px !important;
        border-radius: 50% !important;
        border: none !important;
        background-color: transparent !important;
        font-size: 20px !important;
        margin-top: -42px !important; /* The magic 'pull up' number */
    }
    
    /* Hide the gap between columns */
    [data-testid="column"] {
        width: min-content !important;
        flex: unset !important;
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
    
    loc_choice = st.selectbox("Location", ["+ Add New Location"] + all_locs, 
                              index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New Location" else loc_choice
    
    cat_choice = st.selectbox("Category", ["+ Add New Category"] + global_cats, 
                              index=global_cats.index(current_cat)+1 if current_cat in global_cats else 0)
    final_cat = st.text_input("New Category Name") if cat_choice == "+ Add New Category" else cat_choice
    
    new_note = st.text_area("Note (Optional)")

    if st.button("Save to Inventory", use_container_width=True):
        if new_name and final_loc and final_cat:
            new_row = {
                "category": final_cat, "item_name": new_name, "item_quantity": new_qty,
                "location": final_loc, "last_add_date": datetime.now().strftime("%Y-%m-%d"),
                "last_remove_date": "", "note": new_note
            }
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()

# 4. Main App UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    global_locations = sorted(df['location'].dropna().unique().tolist())
    global_categories = sorted(df['category'].dropna().unique().tolist())
    
    selected_loc = st.selectbox("📍 View Location", global_locations)
    
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    
    default_cat = cats_in_loc[0] if cats_in_loc else ""
    selected_cat = st.pills("Category", cats_in_loc, default=default_cat)

    if st.button("➕ Add New Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, global_locations, global_categories)

    st.divider()

    # Items Display
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            # 1. We build the "Text" part (Name and Qty) in ONE line using Flexbox
            # This is 100% immune to Streamlit's stacking behavior
            item_html = f"""
            <div style="display: flex; align-items: center; width: 100%; font-family: sans-serif;">
                <div style="flex: 4; font-weight: bold; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {row['item_name']}
                </div>
                <div style="flex: 1; text-align: center; font-weight: bold; font-size: 16px;">
                    {int(row['item_quantity'])}
                </div>
                <div style="flex: 2;"></div> </div>
            """
            st.markdown(item_html, unsafe_allow_html=True)

            # 2. We place the buttons in a floating column with a NEGATIVE margin 
            # to pull them up into the row we just created.
            btn_cols = st.columns([5, 1, 1])
            with btn_cols[1]:
                if st.button("🟢", key=f"add_{index}", use_container_width=True):
                    df.at[index, 'item_quantity'] += 1
                    conn.update(data=df)
                    st.rerun()
            with btn_cols[2]:
                if st.button("🔴", key=f"rem_{index}", use_container_width=True):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun()

            # Note row
            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -10px;'>📝 {row['note']}</div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 2px 0; border: none; border-bottom: 1px solid #f0f0f0;'>", unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
