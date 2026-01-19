import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE "GAP KILLER" CSS
st.markdown("""
    <style>
    /* 1. Squeeze the main container padding */
    .block-container {
        padding: 1rem 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* 2. Remove huge vertical gaps between Streamlit elements */
    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }

    /* 3. Force columns to stay side-by-side and remove their padding */
    [data-testid="column"] {
        padding: 0px 2px !important;
        min-width: 0px !important;
        flex: 1 1 auto !important;
    }

    /* 4. Make the buttons small, circular, and centered */
    div[data-testid="stButton"] > button {
        height: 38px !important;
        width: 38px !important;
        border-radius: 50% !important;
        padding: 0px !important;
        margin: 0px auto !important;
        display: block !important;
        border: 1px solid #f0f0f0 !important;
    }

    /* 5. Tighten the Pills/Category selector */
    [data-testid="stElementContainer"] {
        margin-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Connection & Data Loading
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

# 5. Main App UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    g_locs = sorted(df['location'].dropna().unique().tolist())
    g_cats = sorted(df['category'].dropna().unique().tolist())
    
    selected_loc = st.selectbox("📍 Location", g_locs)
    
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    
    default_cat = cats_in_loc[0] if cats_in_loc else ""
    selected_cat = st.pills("Category", cats_in_loc, default=default_cat)

    if st.button("➕ Add New Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, g_locs, g_cats)

    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

    # --- THE COMPACT TABLE-STYLE LIST ---
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            # Row Container
            with st.container():
                # We use 3 columns: [Text Block, Plus Button, Minus Button]
                # Ratio 5:1:1 ensures the name+qty gets most of the space
                c1, c2, c3 = st.columns([5, 1, 1], vertical_alignment="center")
                
                with c1:
                    # This HTML flexbox keeps Name and Qty close together with NO gap
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; justify
