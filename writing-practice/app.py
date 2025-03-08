import streamlit as st
from manga_ocr import MangaOcr
import os
import tempfile
import requests
import random
from dotenv import load_dotenv
from typing import Dict, List
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")

# Initialize MangaOCR
mocr = MangaOcr()

# Constants
API_BASE_URL = "http://localhost:5000"

def fetch_words(group_id: int) -> List[Dict]:
    """Fetch words from lang-portal API"""
    try:
        response = requests.get(f"{API_BASE_URL}/groups/{group_id}/words/raw")
        data = response.json()
        return data.get("words", [])
    except Exception as e:
        st.error(f"Error fetching words: {str(e)}")
        return []

def generate_sentence(word: str) -> str:
    """Generate a simple sentence using the word"""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""Generate a simple Japanese sentence using the following word: {word}
                The grammar should be scoped to JLPTN5 grammar.
                You can use the following vocabulary to construct a simple sentence:
                - simple objects eg. book, car, ramen, sushi
                - simple verbs, to drink, to eat, to meet
                - simple times eg. tomorrow, today, yesterday"""
            }]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        st.write(f"Debug Info: {e}")
        return ""

def grade_writing(image_path: str, target_word: Dict[str, str]) -> Dict:
    """Grade the writing by comparing OCR output with target word"""
    # Transcribe image using MangaOCR
    transcription = mocr(image_path)
    
    # Simple exact match grading
    is_correct = transcription.strip() == target_word["kanji"].strip()
    
    return {
        "transcription": transcription,
        "is_correct": is_correct,
        "target": target_word["kanji"],
        "feedback": "Correct! Well done!" if is_correct else f"Not quite. The correct writing is: {target_word['kanji']}"
    }

# Streamlit UI
st.title("Japanese Writing Practice")

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = 'setup'
    st.session_state.current_word = None
    st.session_state.current_sentence = None
    st.session_state.words = []

# Sidebar for group selection
group_id = st.sidebar.number_input("Group ID", min_value=1, value=1)
if st.sidebar.button("Load Words"):
    st.session_state.words = fetch_words(group_id)
    st.session_state.state = 'setup'
    st.rerun()

# Main content
if len(st.session_state.words) == 0:
    st.warning("Please load a word group using the sidebar.")
else:
    # Setup State
    if st.session_state.state == 'setup':
        if st.button("Generate Practice"):
            # Pick a random word and generate sentence
            st.session_state.current_word = random.choice(st.session_state.words)
            st.session_state.current_sentence = generate_sentence(st.session_state.current_word["english"])
            st.session_state.state = 'practice'
            st.rerun()

    # Practice State
    elif st.session_state.state == 'practice':
        st.write("### English Word")
        st.write(st.session_state.current_word["english"])
        
        st.write("### Japanese Character")
        st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{st.session_state.current_word['kanji']}</h1>", unsafe_allow_html=True)
        
        st.write("### Example Sentence")
        st.write(st.session_state.current_sentence)
        
        st.write("### Write the Japanese character")
        uploaded_file = st.file_uploader("Upload your writing", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                image_path = tmp_file.name
            
            # Grade the writing
            result = grade_writing(image_path, st.session_state.current_word)
            
            # Display results
            st.write("### Results")
            st.write(f"Transcription: {result['transcription']}")
            st.write(f"Target: {result['target']}")
            st.write(result['feedback'])
            
            # Cleanup
            os.unlink(image_path)
            
            if st.button("Try Another"):
                st.session_state.state = 'setup'
                st.rerun()
        
        # Add a button to exit the practice screen
        if st.button("Exit Practice"):
            st.session_state.state = 'setup'
            st.rerun()