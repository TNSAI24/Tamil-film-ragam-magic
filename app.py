import streamlit as st
import pandas as pd
import random  # <-- NEW: Needed for picking random wrong answers

# 1. PAGE SETUP
st.set_page_config(page_title="Tamil Film Ragam Magic", layout="wide", page_icon="🎵")

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
        # First run, show input
        st.text_input(
            "Please enter the Magic Password:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again
        st.text_input(
            "Please enter the Magic Password:", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Access Denied. Try again.")
        return False
    else:
        # Password correct
        return True

if check_password():

    # 3. LOAD DATA
    @st.cache_data
    def load_data():
        df = pd.read_csv("songs_updated.csv")
        # Fill missing links and ensure Ragam is string to avoid errors
        df['Video Link'] = df['Video Link'].fillna("No Link")
        df['The Ragam'] = df['The Ragam'].astype(str)
        return df

    try:
        df = load_data()
        
        st.title("🎵 Tamil Film Ragam Magic")
        st.markdown("Discover the Ragas behind the melodies.")

        tab1, tab2 = st.tabs(["🔎 Search Ragas", "🧠 Challenge Quiz (New!)"])

        # --- TAB 1: SEARCH (UPGRADED) ---
        with tab1:
            st.header("Find Songs by Raga")
            st.write("Type a Raga name to see grouped results.")
            search_term = st.text_input("Search Raga (e.g., 'Kalyani')", placeholder="Type here...")

            if search_term:
                # Filter results (Case insensitive)
                results = df[df['The Ragam'].str.contains(search_term, case=False, na=False)]
                
                if not results.empty:
                    # Get unique Ragam names found
                    unique_ragas = results['The Ragam'].unique()
                    
                    for raga_name in unique_ragas:
                        # Get all songs for this specific Ragam group
                        subset = results[results['The Ragam'] == raga_name]
                        song_count = len(subset)
                        
                        # Main Expander for the Raga
                        with st.expander(f"🎼 **{raga_name}** ({song_count} songs)", expanded=False):
                            
                            # --- NEW Feature: Dropdown list for songs ---
                            # We create a list of song titles for the dropdown
                            song_titles = subset['The Song'].tolist()
                            selected_song_title = st.selectbox(
                                f"Select a song in {raga_name} to play:", 
                                song_titles,
                                key=f"select_{raga_name}" # Unique key for Streamlit
                            )
                            
                            # Find the specific row for the selected song title
                            selected_row = subset[subset['The Song'] == selected_song_title].iloc[0]
                            
                            st.divider()
                            # Show the video and details for the selected song
                            c1, c2 = st.columns([3, 2])
                            with c1:
                                link = str(selected_row['Video Link'])
                                if "http" in link:
                                    st.video(link)
                                else:
                                    st.info("🔸 No Video Link Available yet.")
                            with c2:
                                st.subheader(selected_row['The Song'])
                                st.write(f"🎬 **Film:** {selected_row['The Film Name']}")
                                st.caption(f"🎶 Raga: {selected_row['The Ragam']}")

                else:
                    st.info("Results not found. Try another spelling!")

        # --- TAB 2: QUIZ (UPGRADED WITH HINTS) ---
        with tab2:
            st.header("Test Your Ear!")
            st.write("Click play, listen, and try the hint before revealing the answer!")
            
            # Button to pick a new song
            if st.button("🎲 Play New Mystery Song"):
                # Filter for songs that actually have links
                valid_songs = df[df['Video Link'].str.contains("http", na=False)]
                if not valid_songs.empty:
                    # Sample 1 row
                    mystery = valid_songs.sample(1).iloc[0]
                    # Save to session state so it doesn't disappear
                    st.session_state['quiz_song'] = mystery
                    # Clear old options when picking a new song
                    if 'quiz_options' in st.session_state:
                        del st.session_state['quiz_options']
            
            # Display current puzzle if one exists
            if 'quiz_song' in st.session_state:
                song = st.session_state['quiz_song']
                correct_raga = song['The Ragam']
                
                # Show video without title
                st.video(song['Video Link'])
                
                # --- NEW Feature: Generate Multiple Choice Options ---
                # Only generate if we haven't already for this specific song
                if 'quiz_options' not in st.session_state:
                    # Get a list of all unique ragas
                    all_ragas = df['The Ragam'].unique().tolist()
                    # Remove the correct one from the list just in case
                    possible_wrongs = [r for r in all_ragas if r != correct_raga and r != 'nan']
                    # Pick 2 random wrong answers if enough exist, else fewer
                    num_to_pick = min(len(possible_wrongs), 2)
                    wrong_options = random.sample(possible_wrongs, num_to_pick)
                    
                    # Combine correct + wrong, then shuffle
                    option_list = wrong_options + [correct_raga]
                    random.shuffle(option_list)
                    # Save to session state
                    st.session_state['quiz_options'] = option_list

                # --- Display Hint Section ---
                st.info("👇 Keep scrolling for hints and the answer!")
                with st.expander("💡 Need a Hint? (Multiple Choice)"):
                    st.write("Which one of these do you think it is?")
                    # Use radio buttons for the options
                    user_guess = st.radio(
                        "Make your selection:", 
                        st.session_state['quiz_options'],
                        index=None, # No default selection
                        key="quiz_radio"
                    )
                    
                    if user_guess:
                        if user_guess == correct_raga:
                            st.balloons()
                            st.success("🎉 That's the one! Great ear!")
                        else:
                            st.error("Not quite that one. Try another or reveal the answer!")

                # --- Display Reveal Section ---
                st.divider()
                with st.expander("👀 **Click to Reveal the Final Answer**"):
                    st.markdown(f"### The Raga is: **{correct_raga}**")
                    st.write(f"**Song:** {song['The Song']}")
                    st.write(f"**Film:** {song['The Film Name']}")

    except Exception as e:
        st.error(f"⚠️ Error loading application. Please refresh. Details: {e}")
