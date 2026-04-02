import streamlit as st
from transformers import pipeline

# Load model from hugging face
@st.cache_resource(show_spinner="Loading summarizer model (first use may download ~120MB)…")
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
