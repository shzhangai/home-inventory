import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Pantry", layout="centered")

# 2. THE CSS: This is the only way to force one row on mobile
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Create a horizontal row that will NOT wrap */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
    }

    /* Column 1: Item Name & Qty (Grows to fill space) */
    [data-testid="column"]:nth-of-type(1) {
        flex: 10 !important;
        min-width: 0px !important;
    }

    /* Columns 2 & 3: The Buttons (Stay tiny and on the right) */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) {
        flex: 1 !important;
        max-width: 40px !important;
        min-width: 40px !important;
    }

    /* Make buttons look like simple text/circles */
    div[data-testid="stButton"] > button {
        border: 1px solid #ddd !important;
        background-color: transparent !important;
        padding: 0px !important;
        height: 35px !important;
        width: 35px !important;
        border-radius: 4px !important;
    }

    /* Bold signs inside the buttons */
    [data-testid="stButton"] p {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #333 !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Connection
conn = st.connection("gsheets", type=GSheetsConnection)
if 'df' not in st.session_state:
    st.session_state.df = conn.read(ttl=0)

# 4. Instant Update Fragment
@st.fragment
def show_pantry_list(selected_loc, selected_cat):
    df = st.session_state.df
    items = df[(df['location'] == selected_loc) & (df['category'] == selected_cat)]
    
    for index, row in items.iterrows():
        # These 3 columns are FORCED into one row by the CSS above
        c1, c2, c3 = st.columns([10, 1, 1])
        
        with c1:
            # Inline name and red quantity
            st.markdown(f"""
                <div style="display: flex; align-items: baseline; gap: 8px; overflow: hidden;">
                    <span style="font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['item_name']}</span>
                    <span style="font-size: 15px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
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
        
        st.markdown("<hr style='margin: 4px 0; opacity: 0.1;'>", unsafe_allow_html=True)

# 5. Main UI
st.title("🍎 Pantry Pilot")

if not st.session_state.df.empty:
    locs = sorted(st.session_state.df['location'].dropna().unique().tolist())
    sel_loc = st.selectbox("📍 Location", locs)
    
    cats = sorted(st.session_state.df[st.session_state.df['location'] == sel_loc]['category'].dropna().unique().tolist())
    sel_cat = st.pills("Category", cats, default=cats[0] if cats else None)

    st.divider()
    # This runs instantly without reloading the whole page
    show_pantry_list(sel_loc, sel_cat)
