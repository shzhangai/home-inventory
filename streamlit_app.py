import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. CSS for S24+ Mobile
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force Row Behavior: Prevents stacking on vertical screens */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 5px !important;
    }

    /* Column 1: Name and Qty (takes up remaining space) */
    [data-testid="column"]:nth-of-type(1) { 
        flex: 10 !important; 
        min-width: 0px !important; 
    }
    
    /* Columns 2 & 3: Plus and Minus (fixed small width) */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 0 0 45px !important; 
        min-width: 45px !important; 
    }

    /* Solid Button Styling so they are visible */
    div[data-testid="stButton"] > button {
        border: 1px solid #ddd !important;
        background-color: #f9f9f9 !important;
        color: black !important;
        font-weight: bold !important;
        height: 38px !important;
        width: 38px !important;
        padding: 0px !important;
        border-radius: 5px !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
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
    loc_choice = st.selectbox("Location", ["+ Add New"] + all_locs, index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New" else loc_choice
    cat_choice = st.selectbox("Category", ["+ Add New"] + global_cats, index=global_cats.index(current_cat)+1 if current_cat in global_cats else 0)
    final_cat = st.text_input("New Category Name") if cat_choice == "+ Add New" else cat_choice
    if st.button("Save Item", use_container_width=True):
        if new_name and final_loc and final_cat:
            new_row = {"category": final_cat, "item_name": new_name, "item_quantity": new_qty, "location": final_loc}
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()

# 5. Main UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    g_locs = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    selected_cat = st.pills("Category", cats_in_loc, default=cats_in_loc[0] if cats_in_loc else None)

    if st.button("➕ Add Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, g_locs, sorted(df['category'].dropna().unique().tolist()))

    st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # --- THE LIST ---
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            c1, c2, c3 = st.columns([10, 1, 1])
            
            with c1:
                # Tight Name and Quantity together
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 10px;">
                        <span style="font-size: 14px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 15px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                if st.button("+", key=f"add_{index}"):
                    df.at[index, 'item_quantity'] += 1
                    conn.update(data=df)
                    st.rerun()
            
            with c3:
                if st.button("-", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun()

            st.markdown("<hr style='margin: 4px 0; opacity: 0.1;'>", unsafe_allow_html=True)
else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
