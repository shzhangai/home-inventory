import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Pantry Pilot", layout="centered")

# --- CSS: Minimal and focused only on the horizontal layout ---
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Forces columns to stay in a single row on mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important;
    }

    /* Column 1 (Name + Qty) takes 80% */
    [data-testid="column"]:nth-of-type(1) { flex: 8 !important; }
    
    /* Columns 2 & 3 (Buttons) are restricted to stay close */
    [data-testid="column"]:nth-of-type(2), 
    [data-testid="column"]:nth-of-type(3) { 
        flex: 1 !important; 
        max-width: 45px !important; 
        min-width: 40px !important;
    }

    /* Target the text inside the tertiary buttons to ensure it's black/visible */
    button[kind="tertiary"] {
        color: black !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 0px !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

st.title("🍎 Pantry")

if df is not None and not df.empty:
    # Filter logic (simplified for brevity)
    g_locs = sorted(df['location'].dropna().unique().tolist())
    selected_loc = st.selectbox("📍 Location", g_locs)
    loc_df = df[df['location'] == selected_loc]
    
    st.markdown("---")

    for index, row in loc_df.iterrows():
        # Using 3 columns: [Name+Qty, Plus, Minus]
        c1, c2, c3 = st.columns([8, 1, 1])
        
        with c1:
            # Inline Name and Qty
            st.markdown(f"""
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="font-size: 15px;">{row['item_name']}</span>
                    <span style="font-size: 16px; font-weight: bold; color: #ff4b4b;">{int(row['item_quantity'])}</span>
                </div>
            """, unsafe_allow_html=True)
        
        with c2:
            # use type="tertiary" for a plain text button that is actually visible
            if st.button("+", key=f"add_{index}", type="tertiary"):
                df.at[index, 'item_quantity'] += 1
                conn.update(data=df)
                st.rerun()
        
        with c3:
            if st.button("-", key=f"rem_{index}", type="tertiary"):
                if row['item_quantity'] > 0:
                    df.at[index, 'item_quantity'] -= 1
                    conn.update(data=df)
                    st.rerun()

        st.markdown("<hr style='margin: 0px; opacity: 0.1;'>", unsafe_allow_html=True)
