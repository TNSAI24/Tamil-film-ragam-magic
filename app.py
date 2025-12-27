import streamlit as st
import pandas as pd
import random
import base64

# 1. PAGE SETUP
st.set_page_config(page_title="Tamil Film Ragam Magic", layout="wide", page_icon="🎵")

# --- STYLE FUNCTION: VERSION 4.4 (Golden Cream Fix) ---
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        
        css_code = f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpg;base64,{encoded_string.decode()});
            background-size: cover;
        }}
        
        /* HEADERS (Keep Blue) */
        h1, h2, h3, h4, h5, h6, p, label, span, div, li, a {{
            color: #00008B !important; 
        }}

        /* --- THE GOLDEN CREAM FIX --- */
        /* We use Light Yellow (#FFFACD) to prevent Dark Mode inversion */
        
        /* 1. INPUT BOXES (Typing areas) */
        input {{
            background-color: #FFFACD !important; /* Lemon Chiffon */
            color: #000000 !important; /* Black */
            font-weight: 500;
        }}
        .stTextInput > div > div {{
            background-color: #FFFACD !important;
            color: #000000 !important;
        }}

        /* 2. THE STUBBORN DROPDOWN BOX */
        div[data-baseweb="select"] > div {{
            background-color: #FFFACD !important; /* Lemon Chiffon */
            color: #000000 !important; /* Black */
            border: 1px solid #c0c0c0;
        }}
        
        /* 3. Text inside the dropdown */
        div[data-baseweb="select"] span {{
            color: #000000 !important;
        }}
        /* The Down Arrow */
        div[data-baseweb="select"] svg {{
            fill: #000000 !important;
        }}
        
        /* 4. THE POPUP LIST */
        div[data-baseweb="popover"] {{
            background-color: #FFFACD !important;
        }}
        ul[data-baseweb="menu"] {{
            background-color: #FFFACD !important;
        }}
        li[role="option"] {{
            background-color: #FFFACD !important;
            color: #000000 !important;
        }}
        li[role="option"] div, li[role="option"] span {{
            color: #000000 !important;
        }}
        /* Hover Effect */
        li[role="option"][aria-selected="true"] {{
            background-color: #F0E68C !important; /* Khaki */
            color: #000000 !important;
        }}

        /* REST OF DESIGN */
        .stMarkdown, .stHeader, .stCaption, .stText, .stTextInput {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 10px;
        }}
        button[data-baseweb="tab"] {{
            color: #00008B !important;
            font-weight: bold !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
        }}
        div[role="radiogroup"] {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
        }}
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
        .stAlert {{
            color: #00008B !important;
            background-color: rgba(255, 255, 255, 0.9) !important;
        }}
        </style>
        """
        st.markdown(css_code, unsafe_allow_html=True)

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
                        # PART 2 CONTINUES HERE
                        label_text = f"🎼 **{raga_name}** ({len(subset)} songs)"
                        
                        with st.expander(label_text, expanded=False):
                            song_titles = subset['The Song'].tolist()
                            
                            selected_song_title = st.selectbox(
                                f"Select a song in {raga_name}:", 
                                song_titles, 
                                index=None,  
                                placeholder="Choose a song...",
                                key=f"sel_{raga_name}"
                            )
                            
                            if selected_song_title:
                                selected_row = subset[subset['The Song'] == selected_song_title].iloc[0]
                                st.divider()
                                c1, c2 = st.columns([3, 2])
                                with c1:
                                    link = str(selected_row['Video Link'])
                                    if "http" in link:
                                        st.video(link)
                                    else:
                                        st.info("🔸 No Video Available")
                                with c2:
                                    st.subheader(selected_row['The Song'])
                                    st.write(f"🎬 **Film:** {selected_row['The Film Name']}")
                                    st.caption(f"🎶 Raga: {selected_row['The Ragam']}")
                else:
                    st.info("No ragas found. Try another spelling!")

        # --- TAB 2: SEARCH BY SONG ---
        with tab2:
            st.header("Find Raga by Song")
            song_input = st.text_input("Type a Song Name (e.g., 'Sundari')", placeholder="Type song title...")
            song_search = song_input.strip()
            
            if song_search:
                song_results = df[df['The Song'].str.contains(song_search, case=False, na=False)]
                
                if not song_results.empty:
                    display_options = [f"{row['The Song']} (Movie: {row['The Film Name']})" for index, row in song_results.iterrows()]
                    st.success(f"Found {len(song_results)} matches.")
                    selected_option = st.selectbox(
                        "👇 Select a song from the list to see details:", 
                        display_options, 
                        index=None,  
                        placeholder="Choose a song...",
                        key=f"select_{song_search}"
                    )
                    if selected_option:
                        selection_index = display_options.index(selected_option)
                        selected_row = song_results.iloc[selection_index]
                        st.divider()
                        c1, c2 = st.columns([3, 2])
                        with c1:
                            link = str(selected_row['Video Link'])
                            if "http" in link:
                                st.video(link)
                            else:
                                st.info("🔸 No Video Available")
                        with c2:
                            st.subheader(f"🎵 {selected_row['The Song']}")
                            st.markdown(f"### **Raga: {selected_row['The Ragam']}**")
                            st.write(f"🎬 **Film:** {selected_row['The Film Name']}")
                else:
                    st.warning("No songs found. Try a different keyword.")

        # --- TAB 3: QUIZ ---
        with tab3:
            st.header("Test Your Ear!")
            if st.button("🎲 Play New Mystery Song"):
                valid_songs = df[df['Video Link'].str.contains("http", na=False)]
                if not valid_songs.empty:
                    mystery = valid_songs.sample(1).iloc[0]
                    st.session_state['quiz_song'] = mystery
                    if 'quiz_options' in st.session_state:
                        del st.session_state['quiz_options']
            
            if 'quiz_song' in st.session_state:
                song = st.session_state['quiz_song']
                correct_raga = song['The Ragam']
                st.video(song['Video Link'])
                
                if 'quiz_options' not in st.session_state:
                    all_ragas = df['The Ragam'].unique().tolist()
                    possible_wrongs = [r for r in all_ragas if r != correct_raga and r != 'nan']
                    num_to_pick = min(len(possible_wrongs), 2)
                    wrong_options = random.sample(possible_wrongs, num_to_pick)
                    option_list = wrong_options + [correct_raga]
                    random.shuffle(option_list)
                    st.session_state['quiz_options'] = option_list

                st.info("👇 Keep scrolling for hints!")
                with st.expander("💡 Need a Hint?"):
                    user_guess = st.radio("Pick one:", st.session_state['quiz_options'], index=None, key="quiz_radio")
                    if user_guess:
                        if user_guess == correct_raga:
                            st.balloons()
                            st.success("🎉 Correct!")
                        else:
                            st.error("Not quite. Try again!")
                with st.expander("👀 Reveal Answer"):
                    st.markdown(f"### Raga: **{correct_raga}**")
                    st.write(f"Song: {song['The Song']}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
