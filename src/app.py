import streamlit as st
import nltk
from arxiv_client import get_paper_by_id

st.set_page_config(
    page_title="Paper Distill",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if 'papers' not in st.session_state:
    st.session_state.papers = None
if 'selected_paper_id' not in st.session_state:
    st.session_state.selected_paper_id = None
if 'abstract_summary' not in st.session_state:
    st.session_state.abstract_summary = None
if 'paper_summary' not in st.session_state:
    st.session_state.paper_summary = None
if 'ask_questions_messages' not in st.session_state:
    st.session_state.ask_questions_messages = []
if 'ask_questions_gemini_chat' not in st.session_state:
    st.session_state.ask_questions_gemini_chat = None
if 'ask_questions_gemini_file' not in st.session_state:
    st.session_state.ask_questions_gemini_file = None
if 'ask_questions_chat_paper_id' not in st.session_state:
    st.session_state.ask_questions_chat_paper_id = None

# Download nltk data (if needed)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

st.sidebar.title("How it works")


def open_reference_paper(arxiv_id: str) -> None:
    paper = get_paper_by_id(arxiv_id)
    if paper is None:
        st.error("Unable to load the selected reference paper right now.")
        return

    st.session_state.selected_paper_id = paper.get_short_id()
    st.switch_page("paper_details_page.py")

# Explanation of the paper search
with st.sidebar.expander("**Paper Search**"):
    st.markdown("The paper search uses the arXiv API to search for papers based on a search query and selected categories, \"arXiv is a free distribution service and an open-access archive for nearly 2.4 million scholarly articles in the fields of physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics.\"")
    st.link_button("Learn more about arXiv",
                   "https://info.arxiv.org/about/index.html")

# Explanation of the abstract summarization feature
with st.sidebar.expander("**Abstract Summary**"):
    st.markdown(
        """
        The abstract summary feature created a summarized version of the paper's abstract using a locally run instance of the `sshleifer/distilbart-cnn-12-6` model. This is a distilled version of the `facebook/bart-large-cnn` model. A BART based model which was fine-tuned on the CNN/Daily Mail dataset of news articles and their summaries. \n\n
        The full abstract is passed into the model along with the desired summary length.\n\n
        Distillation is a technique used to reduce the size of a model and subsequently the required compute power while maintaining most of its performance. \n\n 
        BART (Bidirectional and Auto-Regressive Transformers) architecture was developed by Facebook/Meta. It is particularly effective for text summarization tasks as bidirectional encoding and autoregressive decoding work together to understand the context of the text and generate coherent summaries.
        """
    )
    if st.button("Read the BART paper"):
        open_reference_paper("1910.13461")

# Explanation of the paper summary feature
with st.sidebar.expander("**Paper Summary**"):
    st.markdown(
        """
        The paper summary feature summarizes the entire paper based on two user selected parameters, length and technical complexity. The summary is created using `gemini-2.5-flash-lite`, a Large Language Model developed by Google that is accessible through the Gemini Developer API.\n\n
        The paper is downloaded as a pdf, then converted into markdown text, then passed into the model along with a prompt instructing the model to summarize the paper into a certain number of paragraphs at a certain technical complexity. \n\n
        An API is used here rather than a model run locally like in the abstract summary feature due to the fact that scientific papers can be quite long and to summarize one requires a model that can maintain coherence across thousands of tokens. Models like this end up being very large and can be impractical to run locally.\n\n
        Gemini AI architecture excels at processing long-context tasks through specialized attention mechanisms that maintain understanding across thousands of tokens, while innovations like sliding window attention enable efficient referencing of earlier information, making it powerful for analyzing lengthy documents and complex content.
        """
    )
    st.link_button("Gemini model docs (`gemini-2.5-flash-lite`)", "https://ai.google.dev/gemini-api/docs/models")
    if st.button("Read the Gemini 1.5 paper"):
        open_reference_paper("2403.05530")

# Explanation of the ask questions feature
with st.sidebar.expander("**Ask Questions**"):
    st.markdown(
        """
        The ask questions feature is a **multi-turn chat** about the paper using `gemini-2.5-flash-lite` through the Gemini developer API. The full paper PDF is uploaded once (via the Gemini Files API) on the first message so the model can use **multimodal** context, including figures and layout. Follow-up questions stay in the same conversation so earlier answers remain in context.\n\n
        This differs from the paper summary tab, which still converts the PDF to markdown for text-only summarization.
        """
    )
    st.link_button("Gemini model docs (`gemini-2.5-flash-lite`)", "https://ai.google.dev/gemini-api/docs/models")
    if st.button("Read the Gemini 1.5 paper", key="ask_questions_button"):
        open_reference_paper("2403.05530")


search_page = st.Page("search_page.py")
paper_details_page = st.Page("paper_details_page.py")

pg = st.navigation([search_page, paper_details_page], position="hidden")

pg.run()
