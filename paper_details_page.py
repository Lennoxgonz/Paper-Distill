import streamlit as st
from nltk import sent_tokenize
from app import load_summarizer
from google import genai
from google.genai import types
from dotenv import load_dotenv
import pymupdf4llm
import os

# If no paper is selected, navigate back to search page
if st.session_state.selected_paper is None:
    st.switch_page("search_page.py")

# If back button is pressed, set selected paper to None and rerun, taking user back to search page
if st.button("Back to search"):
    st.session_state.selected_paper = None
    st.rerun()

# Putting selected paper into a shorter var name
paper = st.session_state.selected_paper

def paper_pdf_to_markdown():
    # Download paper from arxiv result stored in session state
    paper.download_pdf(filename="paper.pdf")
    # Convert pdf to markdown text and return it
    paper_as_markdown = pymupdf4llm.to_markdown("paper.pdf")
    return paper_as_markdown


load_dotenv()
def summarize_paper(length, complexity):
    # System instructions and defining client
    sys_instruct = f"Condense this academic paper into a summary with a length of {length} paragraphs with a technical complexity level of {complexity}"
    client = genai.Client(api_key=os.environ.get("GOOGLE_STUDIO_API_KEY"))
    # Getting paper as markdown and calling the google genai client with prompts
    paper_as_markdown = paper_pdf_to_markdown()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct),
        contents=[paper_as_markdown]
    )
    # Saving response into session state
    st.session_state.paper_summary = response.text

# Loading summarization model which is stored in streamlit cache
summarizer = load_summarizer()
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

    # Generate abstract summary
    summary = summarizer(
        abstract, max_length=max_length, min_length=max_length - 25, do_sample=False
    )[0]["summary_text"]
    # Save abstract summary into session state
    st.session_state.abstract_summary = summary

# Basic info about paper
with st.container():
    # Title
    st.header(paper.title)
    
    # Authors section
    authors_text = ", ".join([a.name for a in paper.authors][:3])
    if len(paper.authors) > 3:
        authors_text += " et al."
    st.markdown(f"**Authors:** *{authors_text}*")
    
    # Other info
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
    # On button click generate summary call summarize_abstract which stores summary in session state
    if st.button("Generate Abstract Summary", key="abstract_suummary_button"):
        with st.spinner("Generating abstract summary..."):
            summarize_abstract(paper.summary)
    # If abstract summary exists in session state, display it
    if st.session_state.abstract_summary is not None:
        st.markdown(st.session_state.abstract_summary)


# Paper summary tab
with tabs[2]:
    # Get user input for summary parameters
    length = st.slider("Summary Length", 1, 15)
    technical_complexity = st.select_slider(
        "Summary Complexity",
        options=[
            "Simple",
            "Standard",
            "Technical"
        ])
    # Handle submit button, call summarize_paper with parameters which updates session state
    if st.button("Generate Paper Summary", key="paper_summary_button"):
        with st.spinner(f"Generating {technical_complexity} paper summary..."):
            summarize_paper(length, technical_complexity)
    # If there has been a sumary generated and stored in session state, display it
    if st.session_state.paper_summary is not None:
        st.markdown(st.session_state.paper_summary)