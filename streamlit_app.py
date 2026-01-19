import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Home Inventory", layout="centered")

# 1. INITIALIZE STATE
if "needs_sync" not in st.session_state:
    st.session_state["needs_sync"] = False

conn = st.connection("gsheets", type=GSheetsConnection)

if "df" not in st.session_state:
    try:
        # Load the data
        fetched_df = conn.read(ttl=0)
        # CRITICAL SAFETY: Only load if the sheet isn't actually empty
        if fetched_df is not None and not fetched_df.empty:
            st.session_state.df = fetched_df
        else:
            st.error("The Google Sheet appears to be empty. Please restore it from Version History.")
            st.stop()
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

# 2. THE SAFETY SYNC FUNCTION
def safe_sync_to_cloud():
    current_df = st.session_state.df
    
    # SAFETY GATE: Never save if the dataframe is empty or missing columns
    if current_df is None or current_df.empty or len(current_df.columns) < 2:
        st.error("🚨 SYNC BLOCKED: The data is empty. Restoring from cloud instead of saving.")
        st.session_state.df = conn.read(ttl=0)
        st.session_state["needs_sync"] = False
    else:
        conn.update(data=current_df)
        st.session_state["needs_sync"] = False
        st.toast("✅ Cloud Updated Safely!")

def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state["needs_sync"] = True

# 3. MOBILE CSS
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; }
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; min-width: 0px !important; }
    [data-testid="column"]:nth-of-type(2), [data-testid="column"]:nth-of-type(3) { flex: 1 !important; max-width: 45px !important; min-width: 45px !important; }
    button { height: 40px !important; width: 40px !important; padding: 0px !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# 4. UI
st.title("🏠 Home Inventory")

if st.session_state.get("needs_sync", False):
    # Uses the new Safe Sync function
    st.button("💾 SAVE TO CLOUD", on_click=safe_sync_to_cloud, use_container_width=True, type="primary")

df = st.session_state.df
if df is not None and not df.empty:
    all_locs = sorted(df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", all_locs)
    
    cat_options = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cat_options, default=cat_options[0] if cat_options else None)

    st.divider()

    items = df[(df['location'] == sel_loc) & (df['category'] == sel_cat)]
    
    for index, row in items.iterrows():
        c1, c2, c3 = st.columns([8, 1, 1])
        with c1:
            st.markdown(f"**{row['item_name']}** <span style='color:red; font-weight:bold; margin-left:8px;'>{int(row['item_quantity'])}</span>", unsafe_allow_html=True)
        with c2:
            st.button("＋", key=f"add_{index}", on_click=update_qty, args=(index, 1))
        with c3:
            st.button("－", key=f"rem_{index}", on_click=update_qty, args=(index, -1))
        st.markdown("<hr style='margin:4px 0; opacity:0.1;'>", unsafe_allow_html=True)
