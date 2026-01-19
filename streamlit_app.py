import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Optimized for S24+ to kill gaps and prevent stacking
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force Row Behavior */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* Column Widths: 80% for the Info, 10% each for buttons */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { flex: 1 !important; min-width: 35px !important; }

    /* Button Styling (Standard Plus/Minus) */
    div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        font-size: 22px !important;
        padding: 0px !important;
        margin: 0px !important;
        height: 35px !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# 4. Dialog
@st.dialog("Add New Item")
def add_item_dialog(current_loc, current_cat, all_locs, global_cats):
    new_name = st.text_input("Item Name")
    new_qty = st.number_input("Quantity", min_value=0, value=1)
    loc_choice = st.selectbox("Location", ["+ Add New"] + all_locs, index=all_locs.index(current_loc)+1 if current_loc in all_locs else 0)
    final_loc = st.text_input("New Location") if loc_choice == "+ Add New" else loc_choice
    cat_choice = st.selectbox("Category", ["+ Add New"] + global_cats, index=global_cats.index(current_cat)+1 if current_cat in global_cats else 0)
    final_cat = st.text_input("New Category") if cat_choice == "+ Add New" else cat_choice
    if st.button("Save", use_container_width=True):
        new_row = {"category": final_cat, "item_name": new_name, "item_quantity": new_qty, "location": final_loc, "last_add_date": datetime.now().strftime("%Y-%m-%d")}
        updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        conn.update(data=updated_df)
        st.rerun()

# 5. Main UI
st.title("🍎 Family Inventory")

if df is not None and not df.empty:
    g_locs = sorted(df['location'].dropna().unique().tolist())
    g_cats = sorted(df['category'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    loc_df = df[df['location'] == selected_loc]
    cats_in_loc = sorted(loc_df['category'].dropna().unique().tolist())
    selected_cat = st.pills("Category", cats_in_loc, default=cats_in_loc[0] if cats_in_loc else None)

    if st.button("➕ Add Item", use_container_width=True):
        add_item_dialog(selected_loc, selected_cat, g_locs, g_cats)

    st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # --- THE COMPACT LIST ---
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            # We use 3 columns now. Col 1 holds BOTH the Name and Quantity
            c1, c2, c3 = st.columns([8, 1, 1])
            
            with c1:
                # This HTML puts the Quantity IMMEDIATELY after the name with a 10px gap
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 10px;">
                        <span style="font-size: 15px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 16px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                if st.button("➕", key=f"add_{index}"):
                    df.at[index, 'item_quantity'] += 1
                    conn.update(data=df)
                    st.rerun()
            
            with c3:
                if st.button("➖", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun()

            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.caption(f"📝 {row['note']}")
            st.markdown("<hr style='margin: 2px 0; opacity: 0.1;'>", unsafe_allow_html=True)
