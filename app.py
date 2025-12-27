import streamlit as st
import pandas as pd
import random
import base64

# 1. PAGE SETUP
st.set_page_config(page_title="Tamil Film Ragam Magic", layout="wide", page_icon="🎵")

# --- STYLE FUNCTION: VERSION 3.2 (White Backgrounds for Inputs) ---
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpg;base64,{encoded_string.decode()});
            background-size: cover;
        }}
        
        /* --- UNIVERSAL BLUE TEXT --- */
        h1, h2, h3, h4, h5, h6, p, label, span, div, li, a {{
            color: #00008B !important; /* Dark Blue */
        }}

        /* --- INPUT FIELDS & DROPDOWNS (THE FIX) --- */
        /* Force the box where you type to be WHITE background with BLUE text */
        input {{
            color: #00008B !important;
            background-color: #ffffff !important; /* Force White Background */
        }}
        
        /* Specific fix for Streamlit Text Input Containers */
        .stTextInput > div > div {{
            background-color: #ffffff !important;
            color: #00008B !important;
        }}

        /* Specific fix for Dropdown/Selectbox Containers */
        div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
            color: #00008B !important;
        }}
        
        /* Ensure the text inside the dropdown is visible */
        div[data-baseweb="select"] span {{
            color: #00008B !important;
        }}

        /* --- BACKGROUND BOXES --- */
        .stMarkdown, .stHeader, .stCaption, .stText {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 10px;
        }}
        
        /* --- TAB HEADERS --- */
        button[data-baseweb="tab"] {{
            color: #00008B !important;
            font-weight: bold !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
        }}
        
        /* --- QUIZ & RADIO BUTTONS --- */
        div[role="radiogroup"] {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
        }}
        
        /* --- EXPANDERS --- */
        .streamlit-expanderHeader {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #00008B !important;
            border-radius: 10px;
        }}
        .stExpander {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            color: #00008B !important;
        }}
        
        /* --- ALERTS --- */
        .stAlert {{
            color: #00008B !important;
            background-color: rgba(255, 255, 255, 0.9) !important;
        }}
        
        </style>
        """,
        unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"⚠️ Could not find {image_file}. Please ensure 'background.jpg' is uploaded to GitHub.")

# 2. PASSWORD CHECK
def check_password():
    def password_entered():
        if st.session_state["password"].strip() == "Raja123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Please enter the Magic Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Please enter the Magic Password:", type="password", on_change=password_entered, key="password")
        st.error("😕 Access Denied. Try again.")
        return False
    else:
        return True

if check_password():
    add_bg_from_local('background.jpg')

    # 3. LOAD DATA
    @st.cache_data
    def load_data():
        df = pd.read_csv("songs_updated.csv")
        df['Video Link'] = df['Video Link'].fillna("No Link")
        df['The Ragam'] = df['The Ragam'].astype(str)
        df['The Song'] = df['The Song'].astype(str)
        return df

    try:
        df = load_data()
        
        st.title("🎵 Tamil Film Ragam Magic")
        st.markdown("**Discover the Ragas behind the melodies.**")

        tab1, tab2, tab3 = st.tabs(["🔎 Search by Raga", "🎵 Search by Song", "🧠 Quiz"])

        # --- TAB 1: SEARCH BY RAGA ---
        with tab1:
            st.header("Find Songs by Raga")
            search_input = st.text_input("Type a Raga Name (e.g., 'Kalyani')", placeholder="Type here...")
            search_term = search_input.strip()

            if search_term:
                results = df[df['The Ragam'].str.contains(search_term, case=False, na=False)]
                
                if not results.empty:
                    unique_ragas = results['The Ragam'].unique()
                    for raga_name in unique_ragas:
                        subset = results[results['The Ragam'] == raga_name]
                        with st.expander(f"🎼 **{raga_name}** ({len(
