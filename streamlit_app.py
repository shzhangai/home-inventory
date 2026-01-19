import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# Custom CSS for a tight mobile UI
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force the button columns to stay side-by-side and float right */
    [data-testid="stHorizontalBlock"] {
        width: 80px !important;
        float: right !important;
        margin-top: -32px !important; /* Pulls buttons up into the name line */
        z-index: 999;
    }
    
    [data-testid="column"] {
        width: 40px !important;
        flex: none !important;
    }

    div[data-testid="stButton"] > button {
        height: 30px !important;
        width: 30px !important;
        padding: 0px !important;
        border-radius: 50% !important;
        background-color: transparent !important;
        border: none !important;
        font-size: 20px !important;
    }
    
    /* Remove the default gap Streamlit adds to everything */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
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
            
            # 1. THE TEXT WRAPPER
            # We use a container to keep the text and buttons from drifting
            with st.container():
                # We create the Name and Qty as a background layer
                st.markdown(f"""
                    <div style="display: flex; align-items: center; padding-top: 10px;">
                        <div style="flex: 5; font-weight: bold; font-size: 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            {row['item_name']}
                        </div>
                        <div style="flex: 1; text-align: center; font-weight: bold; font-size: 16px; margin-right: 80px;">
                            {int(row['item_quantity'])}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # 2. THE BUTTONS
                # We use a tiny column set that is "pulled up" via CSS
                # By using only 2 columns here, we reduce the 'stacking' risk
                c_btn1, c_btn2 = st.columns([1, 1])
                
                # We use a helper div to float these to the right
                with c_btn1:
                    if st.button("🟢", key=f"add_{index}"):
                        df.at[index, 'item_quantity'] += 1
                        conn.update(data=df)
                        st.rerun()
                with c_btn2:
                    if st.button("🔴", key=f"rem_{index}"):
                        if row['item_quantity'] > 0:
                            df.at[index, 'item_quantity'] -= 1
                            conn.update(data=df)
                            st.rerun()

                # 3. THE NOTE
                if pd.notna(row['note']) and str(row['note']).strip() != "":
                    st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -12px; margin-bottom: 5px;'>📝 {row['note']}</div>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 0; border: none; border-bottom: 1px solid #eee;'>", unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
