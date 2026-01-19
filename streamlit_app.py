import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. CSS for Mobile Density
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    .pantry-label { font-size: 16px; font-weight: 500; }
    .qty-label { font-size: 18px; font-weight: 900; color: #ff4b4b; margin-left: 8px; }
    hr { margin: 8px 0 !important; opacity: 0.1; }
    /* Keeping the segmented control tight */
    div[data-testid="stHorizontalBlock"] { align-items: center; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection & Session State
conn = st.connection("gsheets", type=GSheetsConnection)

# Load data into memory if not already there
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)
    # Track if we have unsaved changes
    st.session_state.needs_sync = False

# 4. Save Function (To prevent the 429 error)
def save_to_sheets():
    try:
        conn.update(data=st.session_state.df)
        st.session_state.needs_sync = False
        st.toast("✅ Synced to Google Sheets!")
    except Exception as e:
        st.error(f"Sync failed: {e}")

# 5. UI Build
st.title("🍎 Pantry Pilot")

# SYNC BUTTON - Only shows if there are changes to save
if st.session_state.needs_sync:
    if st.button("💾 SAVE CHANGES TO CLOUD", use_container_width=True, type="primary"):
        save_to_sheets()

if not st.session_state.df.empty:
    all_locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", all_locs)
    
    cat_options = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cat_options, default=cat_options[0] if cat_options else None)

    st.divider()

    # 6. Fragment for Instant Local Updates
    @st.fragment
    def pantry_list():
        # Filter local session data
        df = st.session_state.df
        items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
        
        for index, row in items.iterrows():
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                st.markdown(f'<span class="pantry-label">{row["item_name"]}</span><span class="qty-label">{int(row["item_quantity"])}</span>', unsafe_allow_html=True)
            
            with col_right:
                action = st.segmented_control(
                    label=f"act_{index}",
                    options=["-1", "+1"],
                    selection_mode="single",
                    key=f"btn_{index}",
                    label_visibility="collapsed"
                )
                
                # Update LOCAL state only (Lightning fast, no API calls)
                if action == "+1":
                    st.session_state.df.at[index, 'item_quantity'] += 1
                    st.session_state.needs_sync = True
                    st.rerun(scope="fragment")
                elif action == "-1":
                    if row['item_quantity'] > 0:
                        st.session_state.df.at[index, 'item_quantity'] -= 1
                        st.session_state.needs_sync = True
                    st.rerun(scope="fragment")
            
            st.markdown("<hr>", unsafe_allow_html=True)

    pantry_list()

else:
    st.info("No data found.")
