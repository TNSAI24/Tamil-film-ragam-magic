import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Tamil Film Ragam Magic", layout="wide")

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
        # Read the CSV file from the repository
        df = pd.read_csv("songs_updated.csv")
        # Fill missing links to avoid crashes
        df['Video Link'] = df['Video Link'].fillna("No Link")
        return df

    try:
        df = load_data()
        
        st.title("🎵 Tamil Film Ragam Magic")
        st.markdown("Discover the Ragas behind the melodies.")

        # TABS: We create two separate sections
        tab1, tab2 = st.tabs(["🔎 Search Ragas", "🧠 Challenge Quiz"])

        # --- TAB 1: SEARCH ---
        with tab1:
            st.header("Find Songs by Raga")
            search_term = st.text_input("Type a Raga Name (e.g., 'Kalyani')")

            if search_term:
                # Filter results (Case insensitive)
                results = df[df['The Ragam'].str.contains(search_term, case=False, na=False)]
                
                if not results.empty:
                    # Group by unique Raga names (e.g. Kalyani vs Yamuna Kalyani)
                    unique_ragas = results['The Ragam'].unique()
                    
                    for raga_name in unique_ragas:
                        # Create a collapsible section for each Raga
                        with st.expander(f"🎼 {raga_name} ({len(results[results['The Ragam'] == raga_name])} songs)", expanded=True):
                            
                            subset = results[results['The Ragam'] == raga_name]
                            
                            for index, row in subset.iterrows():
                                c1, c2 = st.columns([1, 2])
                                with c1:
                                    link = str(row['Video Link'])
                                    if "http" in link:
                                        st.video(link)
                                    else:
                                        st.write("🔸 No Video Available")
                                with c2:
                                    st.subheader(row['The Song'])
                                    st.write(f"🎬 **Film:** {row['The Film Name']}")
                                    st.caption(f"🎶 Raga: {row['The Ragam']}")
                                st.divider()
                else:
                    st.info("No ragas found with that name. Try another spelling!")

        # --- TAB 2: QUIZ ---
        with tab2:
            st.header("Test Your Ear!")
            if st.button("🎲 Play a Mystery Song"):
                # Pick a random song that HAS a video link
                valid_songs = df[df['Video Link'].str.contains("http", na=False)]
                
                if not valid_songs.empty:
                    mystery = valid_songs.sample(1).iloc[0]
                    st.session_state['quiz_song'] = mystery
            
            if 'quiz_song' in st.session_state:
                song = st.session_state['quiz_song']
                
                st.write("Listen to this... can you guess the Raga?")
                # Show video without the title!
                st.video(song['Video Link'])
                
                with st.expander("👀 Click to Reveal Answer"):
                    st.success(f"**Raga:** {song['The Ragam']}")
                    st.write(f"Song: {song['The Song']} ({song['The Film Name']})")

    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
