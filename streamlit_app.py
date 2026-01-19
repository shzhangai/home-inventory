import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Solid circles for buttons to ensure visibility
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force row behavior for items */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 5px !important;
    }

    /* Column 1 (Name + Qty) */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    
    /* Columns 2 & 3 (The Buttons) */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 42px !important;
    }

    /* MAKE BUTTONS VISIBLE CIRCLES */
    [data-testid="stHorizontalBlock"] button {
        height: 40px !important;
        width: 40px !important;
        border-radius: 50% !important;
        padding: 0px !important;
        margin: 0px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        border: none !important;
    }

    /* Style the Plus Button (Green background, White text) */
    [data-testid="column"]:nth-of-type(2) button { background-color: #28a745 !important; }
    [data-testid="column"]:nth-of-type(2) button p { color: white !important; font-size: 24px !important; font-weight: bold !important; }

    /* Style the Minus Button (Red background, White text) */
    [data-testid="column"]:nth-of-type(3) button { background-color: #dc3545 !important; }
    [data-testid="column"]:nth-of-type(3) button p { color: white !important; font-size: 24px !important; font-weight: bold !important; }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Add Item Dialog
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

# 5. Fast Update Fragment
@st.fragment
def pantry_list_view(sel_loc, sel_cat):
    df = st.session_state.df
    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        c1, c2, c3 = st.columns([8, 1, 1])
        with c1:
            st.markdown(f"""
                <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 8px;">
                    <span style="font-size: 16px; font-weight: 500;">{row['item_name']}</span>
                    <span style="font-size: 16px; font-weight: 900; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            if st.button("+", key=f"add_{index}"):
                st.session_state.df.at[index, 'item_quantity'] += 1
                conn.update(data=st.session_state.df)
                st.rerun(scope="fragment")
        with c3:
            if st.button("-", key=f"rem_{index}"):
                if row['item_quantity'] > 0:
                    st.session_state.df.at[index, 'item_quantity'] -= 1
                    conn.update(data=st.session_state.df)
                    st.rerun(scope="fragment")
        st.divider()

# 6. Main UI Build
st.title("🍎 Pantry Pilot")

if not st.session_state.df.empty:
    all_locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    all_cats = sorted(st.session_state.df['category'].dropna().unique().tolist())
    
    sel_loc = st.selectbox("📍 Location", all_locs)
    
    cat_options = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cat_options, default=cat_options[0] if cat_options else None)

    # Restored "Add New Item" Button
    if st.button("➕ Add New Item", use_container_width=True, type="primary"):
        add_item_dialog(sel_loc, sel_cat, all_locs, all_cats)

    st.divider()
    pantry_list_view(sel_loc, sel_cat)
