import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE "GAP KILLER" CSS
st.markdown("""
    <style>
    .block-container {
        padding: 1rem 0.5rem !important;
        max-width: 100% !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    [data-testid="column"] {
        padding: 0px 2px !important;
        min-width: 0px !important;
        flex: 1 1 auto !important;
    }
    div[data-testid="stButton"] > button {
        height: 38px !important;
        width: 38px !important;
        border-radius: 50% !important;
        padding: 0px !important;
        margin: 0px auto !important;
        display: block !important;
        border: 1px solid #f0f0f0 !important;
    }
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
            st.success("Added!")
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
            
            with st.container():
                c1, c2, c3 = st.columns([5, 1, 1], vertical_alignment="center")
                
                with c1:
                    # Using an f-string with single quotes inside to avoid triple-quote confusion
                    item_label = f'<div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">' \
                                 f'<div style="font-weight: bold; font-size: 14px; overflow: hidden;">{row["item_name"]}</div>' \
                                 f'<div style="font-weight: bold; font-size: 16px; padding-right: 10px;">{int(row["item_quantity"])}</div>' \
                                 f'</div>'
                    st.markdown(item_label, unsafe_allow_html=True)
                
                with c2:
                    if st.button("🟢", key=f"add_{index}", use_container_width=True):
                        df.at[index, 'item_quantity'] += 1
                        conn.update(data=df)
                        st.rerun()
                
                with c3:
                    if st.button("🔴", key=f"rem_{index}", use_container_width=True):
                        if row['item_quantity'] > 0:
                            df.at[index, 'item_quantity'] -= 1
                            conn.update(data=df)
                            st.rerun()

                if pd.notna(row['note']) and str(row['note']).strip() != "":
                    st.markdown(f"<div style='font-size: 12px; color: gray; margin-top: -5px;'>📝 {row['note']}</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='border-bottom: 1px solid #f0f2f6; margin-bottom: 4px; margin-top: 4px;'></div>", unsafe_allow_html=True)

else:
    st.info("Pantry is empty!")
    if st.button("➕ Add First Item"):
        add_item_dialog("", "", [], [])
