import streamlit as st
from transformers import pipeline
import nltk

# Initialize session state
if 'papers' not in st.session_state:
    st.session_state.papers = None
if 'selected_paper' not in st.session_state:
    st.session_state.selected_paper = None
if 'abstract_summary' not in st.session_state:
    st.session_state.abstract_summary = None
if 'paper_summary' not in st.session_state:
    st.session_state.paper_summary = None

# Load model from hugging face
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


summarizer = load_summarizer()

# Download nltk data (if needed)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# Define pages
search_page = st.Page("search_page.py")
paper_details_page = st.Page("paper_details_page.py")

# Define nav and hide it
pg = st.navigation([search_page, paper_details_page], position="hidden")

pg.run()
