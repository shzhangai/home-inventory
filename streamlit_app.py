import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Optimized for Speed (Buttons) and Layout (S24+)
st.markdown("""
    <style>
    /* Remove default padding for a tight mobile look */
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force columns to stay in a single row without stacking */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important;
    }

    /* Column 1 (Name + Qty) takes 80% width */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    
    /* Columns 2 & 3 (The Buttons) are small and fixed */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 40px !important;
    }

    /* Target buttons in the list to remove the 'box' look */
    [data-testid="stHorizontalBlock"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
        height: 40px !important;
        width: 40px !important;
    }

    /* Ensure the emojis inside buttons are large */
    [data-testid="stHorizontalBlock"] button p {
        font-size: 22px !important;
        line-height: 1 !important;
    }

    /* Remove the hover/grey circles on touch */
    [data-testid="stHorizontalBlock"] button:hover, 
    [data-testid="stHorizontalBlock"] button:active,
    [data-testid="stHorizontalBlock"] button:focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Keep vertical gaps tight */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* Ensure the main 'Add New Item' button still looks like a real button */
    button[kind="secondaryFormSubmit"], button[kind="primary"], [data-testid="stForm"] button {
        background-color: #f0f2f6 !important;
        border: 1px solid #ddd !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Data Connection
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
            # We use columns for the layout but the CSS forces them into one row
            c1, c2, c3 = st.columns([8, 1, 1])
            
            with c1:
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 8px;">
                        <span style="font-size: 15px; font-weight: 500;">{row['item_name']}</span>
                        <span style="color: #ff4b4b; font-weight: 800; font-size: 16px;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                # Using ➕ emoji ensures visibility and color on mobile
                if st.button("➕", key=f"add_{index}"):
                    df.at[index, 'item_quantity'] += 1
                    conn.update(data=df)
                    st.rerun()
            
            with c3:
                # Using ➖ emoji ensures visibility and color on mobile
                if st.button("➖", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun()

            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -5px;'>📝 {row['note']}</div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 8px 0; opacity: 0.1;'>", unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
