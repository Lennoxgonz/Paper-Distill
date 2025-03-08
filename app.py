import streamlit as st
from transformers import pipeline
import nltk
import arxiv

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

# Sidebar how it works section
st.sidebar.title("How it works")
with st.sidebar.expander("**Abstract Summarization**"):
    # Explanation of the abstract summarization
    st.markdown(
        """
        Creates a summarized version of the paper's abstract using the `sshleifer/distilbart-cnn-12-6` model. This is a distilled version of the `facebook/bart-large-cnn` model. 
        A BART based model which was fine-tuned on the CNN/Daily Mail dataset of news articles and their summaries. \n\n
        Distillation is a technique used to reduce the size of a model and subsequently the required compute power while maintaining most of its performance. \n\n 
        BART(Bidirectional and Auto-Regressive Transformers) architecture was developed by Facebook/Meta and is particularly effective for text summarization tasks as bidirectional encoding and autoregressive decoding work together to understand the context of the text and generate coherent summaries.
        """
    )
    # Button to learn more about BART, takes user to paper details page of original BART paper
    if st.button("Learn more about BART"):
        search = arxiv.Search(id_list=["1910.13461"])
        st.session_state.selected_paper = next(search.results())
        st.switch_page("paper_details_page.py")



# Define pages
search_page = st.Page("search_page.py")
paper_details_page = st.Page("paper_details_page.py")

# Define nav and hide it
pg = st.navigation([search_page, paper_details_page], position="hidden")

pg.run()
