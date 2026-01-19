import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Optimized for Speed (Buttons) and Layout (S24+)
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force columns to stay in a single row without stacking */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important;
    }

    /* Column 1 (Name + Qty) */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    
    /* Columns 2 & 3 (The Buttons) */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 40px !important;
    }

    /* Target standard buttons to make them look like plain colored text */
    div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        font-size: 28px !important;
        font-weight: bold !important;
        padding: 0px !important;
        margin: 0px !important;
        height: 35px !important;
        width: 35px !important;
    }

    /* Remove the hover box/grey background */
    div[data-testid="stButton"] > button:hover, 
    div[data-testid="stButton"] > button:active, 
    div[data-testid="stButton"] > button:focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Specific colors for our keys */
    [data-testid="stButton"] button p { font-size: 28px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 4. Add Item Dialog
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

    if st.button("Save Item", use_container_width=True):
        if new_name and final_loc and final_cat:
            new_row = {
                "category": final_cat, "item_name": new_name, "item_quantity": new_qty,
                "location": final_loc, "last_add_date": datetime.now().strftime("%Y-%m-%d"),
                "note": new_note
            }
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()

# 5. Main UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    global_locations = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 View Location", global_locations)
    
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    
    default_cat = cats_in_loc[0] if cats_in_loc else ""
    selected_cat = st.pills("Category", cats_in_loc, default=default_cat)

    if st.button("➕ Add New Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, global_locations, sorted(df['category'].dropna().unique().tolist()))

    st.divider()

    # 6. List Display
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            c1, c2, c3 = st.columns([8, 1, 1])
            
            with c1:
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 10px;">
                        <span style="font-size: 15px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 16px; font-weight: bold; color: #666;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                # Green Plus
                if st.button("+", key=f"add_{index}"):
                    df.at[index, 'item_quantity'] += 1
                    conn.update(data=df)
                    st.rerun()
                st.markdown(f"<style>div[data-testid='stButton'] > button[key='add_{index}'] {{ color: #28a745 !important; }}</style>", unsafe_allow_html=True)
            
            with c3:
                # Red Minus
                if st.button("-", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun()
                st.markdown(f"<style>div[data-testid='stButton'] > button[key='rem_{index}'] {{ color: #dc3545 !important; }}</style>", unsafe_allow_html=True)

            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -5px;'>📝 {row['note']}</div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 8px 0; opacity: 0.1;'>", unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
