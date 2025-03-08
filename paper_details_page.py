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



# Load summarization model which is stored in streamlit cache
summarizer = load_summarizer()
def summarize_abstract(length):

    # Get abstract and its length from paper
    abstract = paper.summary
    abstract_length = len(abstract.split())

    # Convert length from percentage to number of words and return an iteger
    length = round(length / 100 * abstract_length)

    # If abstract is longer than 900 words, shorten it to 900 words
    # This is because the model only has 1024 positional embeddings
    if abstract_length > 900:
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

    # Generate abstract summary with a length padding of 10 in each direction
    # This is to give the model some leeway in generating the summary
    summary = summarizer(
        abstract, max_length=length + 10, min_length=length - 10, do_sample=False
    )[0]["summary_text"]
    # Save abstract summary into session state
    st.session_state.abstract_summary = summary

load_dotenv()
def summarize_paper(length, complexity):
    # System instructions and defining client
    sys_instruct = f"Condense this academic paper into a summary with a length of {length} paragraphs. Write it using vocabulary terms and explanations appropriate for a {complexity} student, but still keep it informative and professional."
    client = genai.Client(api_key=os.environ.get("GOOGLE_STUDIO_API_KEY"))
    # Calling the google genai client with system instructions and paper as markdown
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct),
        contents=[paper_pdf_to_markdown()]
    )
    # Saving response into session state
    st.session_state.paper_summary = response.text

def answer_question(question):
    client = genai.Client(api_key=os.environ.get("GOOGLE_STUDIO_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="Your are the writer of the paper in question, answer the question based on what you know about the paper, politley decline any request not related to the paper.",
        ),
        contents=[paper_pdf_to_markdown(), question]
    )
    return response.text

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
tabs = st.tabs(["Abstract", "Abstract Summary", "Paper Summary", "Ask Questions"])
with tabs[0]:
    st.markdown(paper.summary)
# Abstract summary tab
with tabs[1]:
    length = st.slider(
        "Summary Length(In percentage of original size)", 10, 100)

    # On button click generate summary call summarize_abstract which stores summary in session state
    if st.button("Generate Abstract Summary", key="abstract_summary_button"):
        with st.spinner("Generating abstract summary..."):
            summarize_abstract(length)
    # If abstract summary exists in session state, display it
    if st.session_state.abstract_summary is not None:
        st.markdown(st.session_state.abstract_summary)


# Paper summary tab
with tabs[2]:
    # Get user input for summary parameters
    length = st.slider("Summary Length(In paragraphs)", 1, 15)
    technical_complexity = st.select_slider(
        "Summary Complexity",
        options=[
            "High School",
            "Undergraduate",
            "Graduate",
            "PhD",
        ])
    # Handle submit button, call summarize_paper with parameters which updates session state
    if st.button("Generate Paper Summary", key="paper_summary_button"):
        with st.spinner(f"Generating {technical_complexity} paper summary..."):
            summarize_paper(length, technical_complexity)
    # If there has been a sumary generated and stored in session state, display it
    if st.session_state.paper_summary is not None:
        st.markdown(st.session_state.paper_summary)

# Ask questions tab
with tabs[3]:
    # Get user input for question
    question = st.text_input("Ask a question about the paper", max_chars=500)
    # If question is asked, call google genai client with prompt and paper as markdown
    if st.button("Ask", key="ask_button"):
        if question != "":
            with st.spinner("Generating answer..."):
                answer = answer_question(question)
                st.markdown(answer)
        else:
            st.warning("Please enter a question.")
