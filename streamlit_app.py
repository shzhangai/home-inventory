import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: This forces the columns to be "tight" and removes button padding
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Force columns to NOT expand. They will only take up the space they need */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: flex-start !important; /* Align everything to the left */
        gap: 0px !important;
    }

    /* Column 1 (Name + Qty) takes most space, others are tiny */
    [data-testid="column"]:nth-of-type(1) { flex: 10 !important; }
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        min-width: 40px !important; 
        max-width: 45px !important; 
    }

    /* Make buttons look like plain text/icons with zero extra width */
    div[data-testid="stButton"] > button {
        border: none !important;
        background: transparent !important;
        padding: 0px !important;
        margin: 0px !important;
        width: 30px !important;
        height: 30px !important;
        font-size: 20px !important;
        color: #31333F !important;
    }
    
    /* Remove vertical space between rows */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection & Dialog
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

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

# 4. Main UI
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

    # --- THE COMPACT LIST ---
    for index, row in df.iterrows():
        if row['location'] == selected_loc and row['category'] == selected_cat:
            
            # Using 3 columns. C2 and C3 are forced to be very narrow by CSS above.
            c1, c2, c3 = st.columns([10, 1, 1])
            
            with c1:
                # Tight Name and Quantity
                st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 8px;">
                        <span style="font-size: 14px; font-weight: 500;">{row['item_name']}</span>
                        <span style="font-size: 15px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c2:
                # Use a plain text character inside the button
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

            if pd.notna(row['note']) and str(row['note']).strip() != "":
                st.caption(f"📝 {row['note']}")
            st.markdown("<hr style='margin: 2px 0; opacity: 0.1;'>", unsafe_allow_html=True)
