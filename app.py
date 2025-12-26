import streamlit as st
import pandas as pd
import random
import base64

# 1. PAGE SETUP
st.set_page_config(page_title="Tamil Film Ragam Magic", layout="wide", page_icon="🎵")

# --- STYLE FUNCTION: ADD BACKGROUND IMAGE ---
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
        .stMarkdown, .stHeader {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 10px;
        }}
        .stExpander {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"⚠️ Could not find {image_file}. Please ensure 'background.jpg' is uploaded to GitHub.")

# 2. PASSWORD CHECK
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "Raja123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Please enter the Magic Password:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Please enter the Magic Password:", type="password", on_change=password_entered, key="password"
        )
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
            search_term = st.text_input("Type a Raga Name (e.g., 'Kalyani')", placeholder="Type here...")

            if search_term:
                results = df[df['The Ragam'].str.contains(search_term, case=False, na=False)]
                
                if not results.empty:
                    unique_ragas = results['The Ragam'].unique()
                    for raga_name in unique_ragas:
                        subset = results[results['The Ragam'] == raga_name]
                        with st.expander(f"🎼 **{raga_name}** ({len(subset)} songs)", expanded=False):
                            song_titles = subset['The Song'].tolist()
                            selected_song_title = st.selectbox(f"Select a song in {raga_name}:", song_titles, key=f"sel_{raga_name}")
                            
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

        # --- TAB 2: SEARCH BY SONG (FIXED: No video until selected!) ---
        with tab2:
            st.header("Find Raga by Song")
            song_search = st.text_input("Type a Song Name (e.g., 'Sundari')", placeholder="Type song title...")
            
            if song_search:
                song_results = df[df['The Song'].str.contains(song_search, case=False, na=False)]
                
                if not song_results.empty:
                    display_options = [f"{row['The Song']} (Movie: {row['The Film Name']})" for index, row in song_results.iterrows()]
                    
                    st.success(f"Found {len(song_results)} matches.")
                    
                    # --- NEW LOGIC: index=None makes it empty by default ---
                    selected_option = st.selectbox(
                        "👇 Select a song from the list to see details:", 
                        display_options, 
                        index=None,  # <--- This keeps it empty initially
                        placeholder="Choose a song...",
                        key="song_select_dropdown"
                    )
                    
                    # Only run this part IF the user has actually selected something
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
