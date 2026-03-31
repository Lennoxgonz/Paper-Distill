import streamlit as st
from nltk import sent_tokenize
from google import genai
from google.genai import types
import pymupdf4llm
from utils import load_summarizer
from search_page import categories_dict

if st.session_state.selected_paper is None:
    st.switch_page("search_page.py")

if st.button("Back to search"):
    st.session_state.selected_paper = None
    st.rerun()

paper = st.session_state.selected_paper

def paper_pdf_to_markdown():
    paper.download_pdf(filename="paper.pdf")
    paper_as_markdown = pymupdf4llm.to_markdown("paper.pdf")
    return paper_as_markdown

summarizer = load_summarizer()
def summarize_abstract(length):

    abstract = paper.summary
    abstract_length = len(abstract.split())

    length = round(length / 100 * abstract_length)

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
    st.session_state.abstract_summary = summary

client = genai.Client(api_key=st.secrets["google_ai_studio_api_key"])
GEMINI_MODEL = "gemini-2.5-flash-lite"

def summarize_paper(length, complexity):
    # System instructions for gemini
    sys_instruct = f"Condense this academic paper into a summary with a length of {length} paragraphs. Write it using vocabulary terms and explanations appropriate for a {complexity} student, but still keep it informative and professional. Do not add any formatting or introduction, simply return the requested number of paragraphs of summarized content."
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct),
        contents=[paper_pdf_to_markdown()]
    )
    st.session_state.paper_summary = response.text

def answer_question(question):
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction="You are extremely knowledgeable about the paper in question, answer the question based on what you know about the paper, politley decline any request not related to the paper. At the end of your response suggest 3 related questions to be asked.",
        ),
        contents=[paper_pdf_to_markdown(), question]
    )
    return response.text

with st.container():
    # Title
    st.header(paper.title)

    # Authors section
    authors_text = ", ".join([a.name for a in paper.authors][:3])
    if len(paper.authors) > 3:
        authors_text += " et al."
    st.markdown(f"**Authors:** *{authors_text}*")


col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Published:** {paper.published.strftime('%Y-%m-%d')}")
with col2:
    display_categories = [categories_dict.get(cat, cat) for cat in paper.categories]
    categories_display = ", ".join(display_categories)
    st.markdown(f"**Categories:** {categories_display}")
st.markdown(
    f"**Links:** [PDF]({paper.pdf_url}) | [arXiv]({paper.entry_id})"
)

tabs = st.tabs(["Abstract", "Abstract Summary", "Paper Summary", "Ask Questions"])
with tabs[0]:
    st.markdown(paper.summary)

# Abstract summary tab
with tabs[1]:
    length = st.slider(
        "Summary Length(In percentage of original size)", 10, 100)

    if st.button("Generate Abstract Summary", key="abstract_summary_button"):
        with st.spinner("Generating abstract summary..."):
            summarize_abstract(length)
    if st.session_state.abstract_summary is not None:
        st.markdown(st.session_state.abstract_summary)


# Paper summary tab
with tabs[2]:
    # User input for summary parameters
    length = st.slider("Summary Length(In paragraphs)", 1, 15)
    technical_complexity = st.select_slider(
        "Summary Complexity",
        options=[
            "High School",
            "Undergraduate",
            "Graduate",
            "PhD",
        ])
    if st.button("Generate Paper Summary", key="paper_summary_button"):
        with st.spinner(f"Generating {technical_complexity} level paper summary..."):
            summarize_paper(length, technical_complexity)
    if st.session_state.paper_summary is not None:
        st.markdown(st.session_state.paper_summary)

# Ask questions tab
with tabs[3]:
    # User input for question
    question = st.text_input("Ask a question about the paper(or ask what are good questions to ask)", max_chars=500)
    if st.button("Ask", key="ask_button"):
        if question != "":
            with st.spinner("Generating answer..."):
                answer = answer_question(question)
                st.markdown(answer)
        else:
            st.warning("Please enter a question.")
