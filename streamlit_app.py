import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Fixed colors and restored layout
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* Plus Button Color */
    .btn-plus {
        text-decoration: none !important;
        font-size: 30px !important;
        font-weight: bold !important;
        color: #28a745 !important; /* Solid Green */
        padding: 0 10px !important;
    }
    
    /* Minus Button Color */
    .btn-minus {
        text-decoration: none !important;
        font-size: 30px !important;
        font-weight: bold !important;
        color: #dc3545 !important; /* Solid Red */
        padding: 0 10px !important;
    }
    
    .item-row {
        display: flex; 
        align-items: center; 
        justify-content: flex-start; 
        margin-bottom: 8px; 
        border-bottom: 1px solid #eee; 
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 4. URL Click Logic
params = st.query_params
if "action" in params and "id" in params:
    idx = int(params["id"])
    if params["action"] == "add":
        df.at[idx, 'item_quantity'] += 1
    elif params["action"] == "rem" and df.at[idx, 'item_quantity'] > 0:
        df.at[idx, 'item_quantity'] -= 1
    conn.update(data=df)
    st.query_params.clear()
    st.rerun()

# 5. Add Item Dialog
@st.dialog("Add New Item")
def add_item_dialog(current_loc, current_cat, all_locs, global_cats):
    new_name = st.text_input("Item Name")
    new_qty = st.number_input("Quantity", min_value=0, value=1)
    
    loc_choice = st.selectbox("Location", ["+ Add New"] + all_locs, 
                              index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New" else loc_choice
    
    cat_choice = st.selectbox("Category", ["+ Add New"] + global_cats, 
                              index=global_cats.index(current_cat)+1 if current_cat in global_cats else 0)
    final_cat = st.text_input("New Category Name") if cat_choice == "+ Add New" else cat_choice
    
    new_note = st.text_area("Note (Optional)")

    if st.button("Save to Inventory", use_container_width=True):
        if new_name and final_loc and final_cat:
            new_row = {
                "category": final_cat, "item_name": new_name, "item_quantity": new_qty,
                "location": final_loc, "last_add_date": datetime.now().strftime("%Y-%m-%d"),
                "note": new_note
            }
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()

# 6. Main UI Restored
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

    # 7. List Display
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            # HTML Row
            st.markdown(f"""
                <div class="item-row">
                    <div style="flex-grow: 1; font-size: 15px;">
                        <b>{row['item_name']}</b> 
                        <span style="color: #666; margin-left: 8px; font-weight: 800;">{int(row['item_quantity'])}</span>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <a href="/?action=add&id={index}" target="_self" class="btn-plus">+</a>
                        <a href="/?action=rem&id={index}" target="_self" class="btn-minus">−</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Restored Note display
            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -8px; margin-bottom: 8px;'>📝 {row['note']}</div>", unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
