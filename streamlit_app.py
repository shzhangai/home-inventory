import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry Pilot", layout="centered")

# 2. THE CSS: Solid, visible text-based buttons
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* The Row Container */
    .pantry-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }

    /* Target the buttons specifically */
    div[data-testid="stButton"] > button {
        border: 1px solid #ddd !important; /* Adding a light border back so you can see the target */
        background-color: #f9f9f9 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 40px !important;
        width: 40px !important;
        padding: 0px !important;
        border-radius: 5px !important;
    }

    /* Force Colors on the text symbols */
    .plus-label { color: #28a745 !important; font-weight: 900; font-size: 24px; }
    .minus-label { color: #dc3545 !important; font-weight: 900; font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Instant Update Fragment
@st.fragment
def show_items(selected_loc, selected_cat):
    df = st.session_state.df
    items = df[(df['location'] == selected_loc) & (df['category'] == selected_cat)]
    
    for index, row in items.iterrows():
        # Create a container for the row
        with st.container():
            # Name and Quantity at the top
            st.markdown(f"**{row['item_name']}** : red[{int(row['item_quantity'])}]")
            
            # Plus and Minus buttons side-by-side right under the name
            # We use a very small gap to keep them together
            btn_left, btn_right, _ = st.columns([1, 1, 4])
            
            with btn_left:
                if st.button("＋", key=f"add_{index}"):
                    st.session_state.df.at[index, 'item_quantity'] += 1
                    conn.update(data=st.session_state.df)
                    st.rerun(scope="fragment")
            
            with btn_right:
                if st.button("－", key=f"rem_{index}"):
                    if row['item_quantity'] > 0:
                        st.session_state.df.at[index, 'item_quantity'] -= 1
                        conn.update(data=df)
                        st.rerun(scope="fragment")
            
            st.markdown("---")

# 5. UI Build
st.title("🍎 Family Inventory")

if not st.session_state.df.empty:
    locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    show_items(sel_loc, sel_cat)
