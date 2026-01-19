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
        st.session_state.df = conn.read(ttl=0)
    except Exception as e:
        st.error("Connection failed.")
        st.stop()

# 2. LOGIC
def update_qty(index, delta):
    st.session_state.df.at[index, 'item_quantity'] += delta
    if st.session_state.df.at[index, 'item_quantity'] < 0:
        st.session_state.df.at[index, 'item_quantity'] = 0
    st.session_state["needs_sync"] = True

def safe_sync():
    conn.update(data=st.session_state.df)
    st.session_state["needs_sync"] = False
    st.toast("✅ Saved!")

# 3. UI TOP BAR
st.title("🏠 Home Inventory")

if st.session_state.get("needs_sync", False):
    st.button("💾 SAVE TO CLOUD", on_click=safe_sync, use_container_width=True, type="primary")

df = st.session_state.df
locs = sorted(df['location'].dropna().unique().tolist())
sel_loc = st.selectbox("📍 Location", locs)

cats = sorted(df[df['location'] == sel_loc]['category'].dropna().unique().tolist())
sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

st.divider()

# 4. THE ROW RENDERER
# We are abandoning st.columns and using a custom layout
@st.fragment
def render_list(location, category):
    items = st.session_state.df[
        (st.session_state.df['location'] == location) & 
        (st.session_state.df['category'] == category)
    ]
    
    for index, row in items.iterrows():
        # Using an inner container with custom CSS to prevent any wrapping
        # 'nowrap' is the key instruction here.
        st.markdown(
            f"""
            <div style="
                display: flex;
                flex-direction: row;
                flex-wrap: nowrap;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            ">
                <div style="flex-grow: 1; min-width: 0; margin-right: 10px;">
                    <span style="font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;">
                        {row['item_name']}
                    </span>
                </div>
                <div style="color: red; font-weight: bold; font-size: 1.2rem; margin-right: 15px; flex-shrink: 0;">
                    {int(row['item_quantity'])}
                </div>
                <div style="display: flex; gap: 5px; flex-shrink: 0;">
                    </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # We place the buttons immediately below the HTML label to keep them in the flow
        # but we use columns that are SO small they won't trigger a wrap.
        b_col1, b_col2, b_filler = st.columns([0.2, 0.2, 0.6])
        with b_col1:
            if st.button("＋", key=f"p_{index}"):
                update_qty(index, 1)
                st.rerun(scope="fragment")
        with b_col2:
            if st.button("－", key=f"m_{index}"):
                update_qty(index, -1)
                st.rerun(scope="fragment")
        
        st.markdown("<div style='margin-top:-45px;'></div>", unsafe_allow_html=True)

render_list(sel_loc, sel_cat)
