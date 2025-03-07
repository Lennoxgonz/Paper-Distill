import streamlit as st
from nltk import sent_tokenize
from app import load_summarizer
from google import genai
from dotenv import load_dotenv
import os

# If no paper is selected, navigate back to search page
if st.session_state.selected_paper is None:
    st.switch_page("search_page.py")

# If back button is pressed set selected paper to None and rerun, taking user back to search page
if st.button("Back to search"):
    st.session_state.selected_paper = None
    st.rerun()

summarizer = load_summarizer()

load_dotenv()

client = genai.Client(api_key=os.environ.get("GOOGLE_STUDIO_API_KEY"))
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works",
)

def summarize_abstract(abstract, max_length=100):
    # Handle abstracts that are too long
    if len(abstract.split()) > 900:
        sentences = sent_tokenize(abstract)
        shortened_abstract = ""
        word_count = 0

        for sentence in sentences:
            words = sentence.split()
            if word_count + len(words) <= 900:
                shortened_abstract += sentence + " "
                word_count += len(words)
            else:
                break
        abstract = shortened_abstract

    # Generate summary
    summary = summarizer(
        abstract, max_length=max_length, min_length=max_length - 25, do_sample=False
    )[0]["summary_text"]
    return summary

paper = st.session_state.selected_paper

# Basic info about paper
with st.container():
    st.header(paper.title)
    
    authors_text = ", ".join([a.name for a in paper.authors][:3])
    if len(paper.authors) > 3:
        authors_text += " et al."
    st.markdown(f"**Authors:** *{authors_text}*")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Published:** {paper.published.strftime('%Y-%m-%d')}")
    
    with col2:
        categories = ", ".join(paper.categories)
        st.markdown(f"**Categories:** {categories}")
    
    st.markdown(
        f"**Links:** [PDF]({paper.pdf_url}) | [arXiv]({paper.entry_id})"
    )

# Tabs for abstract and ML features
tabs = st.tabs(["Abstract", "Abstract Summary", "Paper Summary"])
with tabs[0]:
    st.markdown(paper.summary)
# Abstract summary tab
with tabs[1]:
    summary_key = f"summary_{hash(paper.entry_id)}"
    
    # Render button only if summary has not been generated
    if summary_key not in st.session_state:
        # On button click generate summary and store in session state
        if st.button("Generate Summary"):
            try:
                with st.spinner("Generating summary..."):
                    st.session_state[summary_key] = summarize_abstract(
                        paper.summary)
                    st.rerun()
            except Exception as e:
                st.error(f"Error generating summary: {e}")
    
    # Display summary
    if summary_key in st.session_state:
        st.markdown(f"*{st.session_state[summary_key]}*")

# Paper summary tab
with tabs[2]:
    st.markdown(response.text)