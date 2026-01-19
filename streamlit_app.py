import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. Connection and Session State
conn = st.connection("gsheets", type=GSheetsConnection)

if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 3. Add Item Dialog
@st.dialog("Add New Item")
def add_item_dialog(current_loc, current_cat, all_locs, all_cats):
    new_name = st.text_input("Item Name")
    new_qty = st.number_input("Quantity", min_value=0, value=1)
    
    loc_choice = st.selectbox("Location", ["+ Add New"] + all_locs, 
                              index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location Name") if loc_choice == "+ Add New" else loc_choice
    
    cat_choice = st.selectbox("Category", ["+ Add New"] + all_cats, 
                              index=all_cats.index(current_cat)+1 if current_cat in all_cats else 0)
    final_cat = st.text_input("New Category Name") if cat_choice == "+ Add New" else cat_choice
    
    if st.button("Save to Inventory", use_container_width=True):
        if new_name and final_loc and final_cat:
            new_row = {
                "category": final_cat, "item_name": new_name, "item_quantity": new_qty,
                "location": final_loc, "last_add_date": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=st.session_state.df)
            st.rerun()

# 4. Fast Update Fragment
@st.fragment
def pantry_list_view(sel_loc, sel_cat):
    df = st.session_state.df
    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        # Using a very simple 3-column layout without CSS overrides
        c1, c2, c3 = st.columns([6, 2, 2])
        
        with c1:
            # Using bold text and standard markdown for the name/qty
            st.write(f"**{row['item_name']}**")
            st.caption(f"Count: {int(row['item_quantity'])}")
            
        with c2:
            # Plain, standard buttons that won't disappear
            if st.button("＋", key=f"add_{index}", use_container_width=True):
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun(scope="fragment")
                
        with c3:
            if st.button("－", key=f"rem_{index}", use_container_width=True):
                if row['item_quantity'] > 0:
                    st.session_state.df.at[index, 'item_quantity'] -= 1
                    conn.update(data=st.session_state.df)
                    st.rerun(scope="fragment")
        st.divider()

# 5. Main UI Build
st.title("🍎 Pantry Pilot")

if not st.session_state.df.empty:
    all_locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    all_cats = sorted(st.session_state.df['category'].dropna().unique().tolist())
    
    sel_loc = st.selectbox("📍 Location", all_locs)
    
    cat_options = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cat_options, default=cat_options[0] if cat_options else None)

    if st.button("➕ Add New Item", use_container_width=True, type="primary"):
        add_item_dialog(sel_loc, sel_cat, all_locs, all_cats)

    st.divider()
    pantry_list_view(sel_loc, sel_cat)
