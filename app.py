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

# Explanation of the paper search
with st.sidebar.expander("**Paper Search**"):
    st.markdown("The paper search uses the arXiv API to search for papers based on a search query and selected categories, \"arXiv is a free distribution service and an open-access archive for nearly 2.4 million scholarly articles in the fields of physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics.\"")
    st.link_button("Learn more about arXiv",
                   "https://info.arxiv.org/about/index.html")

with st.sidebar.expander("**Abstract Summary**"):
    # Explanation of the abstract summarization
    st.markdown(
        """
        The abstract summary feature created a summarized version of the paper's abstract using a locally run instance of the `sshleifer/distilbart-cnn-12-6` model. This is a distilled version of the `facebook/bart-large-cnn` model. A BART based model which was fine-tuned on the CNN/Daily Mail dataset of news articles and their summaries. \n\n
        The full abstract is passed into the model along with the desired summary length.\n\n
        Distillation is a technique used to reduce the size of a model and subsequently the required compute power while maintaining most of its performance. \n\n 
        BART (Bidirectional and Auto-Regressive Transformers) architecture was developed by Facebook/Meta. It is particularly effective for text summarization tasks as bidirectional encoding and autoregressive decoding work together to understand the context of the text and generate coherent summaries.
        """
    )
    # Button to take user to paper details page of the original BART paper
    if st.button("Read the BART academic paper"):
        search = arxiv.Search(id_list=["1910.13461"])
        st.session_state.selected_paper = next(search.results())
        st.switch_page("paper_details_page.py")

# Explanation of the paper summary feature
with st.sidebar.expander("**Paper Summary**"):
    st.markdown(
        """
        The paper summary feature summarizes the entire paper based on two user selected parameters, length and technical complexity. The summary is created using Gemini 2.0, a Large Language Model developed by Google that is accessible through the Gemini Developer API.\n\n
        The paper is downloaded as a pdf, then converted into markdown text, then passed into the model along with a prompt instructing the model to summarize the paper into a certain number of paragraphs at a certain technical complexity. \n\n
        An API is used here rather than a model run locally like in the abstract summary feature due to the fact that academic papers can be quite long and to summarize one requires a model that can maintain coherence across thousands of tokens. Models like this end up being very large and can be impractical to run locally.\n\n
        Gemini AI architecture excels at processing long-context tasks through specialized attention mechanisms that maintain understanding across thousands of tokens, while innovations like sliding window attention enable efficient referencing of earlier information, making it powerful for analyzing lengthy documents and complex content.
        """
    )
    # Button to take users to the Gemini 2.0 blog post
    st.link_button("Learn more about Gemini 2.0", "https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/#gemini-2-0")
    # Button to take user to paper details page of the gemini 1.5 paper
    if st.button("Read the Gemini 1.5 academic paper"):
        search = arxiv.Search(id_list=["2403.05530"])
        st.session_state.selected_paper = next(search.results())
        st.switch_page("paper_details_page.py")

with st.sidebar.expander("**Ask Questions**"):
    st.markdown(
        """
        The ask questions feature allows users to ask questions about the paper. This is achieved through the use of Gemini 2.0 through the Gemini developer API and works in a very similar way to the paper summary feature.\n\n
        The paper is downloaded as a pdf, converted to markdown, then passed into the model along with the question to be asked and a prompt instructing the model to answer the question based on the context of the paper.
        """
    )
    # Button to take users to the Gemini 2.0 blog post
    st.link_button("Learn more about Gemini 2.0", "https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/#gemini-2-0")
    # Button to take user to paper details page of the gemini 1.5 paper
    if st.button("Read the Gemini 1.5 academic paper", key="ask_questions_button"):
        search = arxiv.Search(id_list=["2403.05530"])
        st.session_state.selected_paper = next(search.results())
        st.switch_page("paper_details_page.py")


# Define pages
search_page = st.Page("search_page.py")
paper_details_page = st.Page("paper_details_page.py")

# Define nav and hide it
pg = st.navigation([search_page, paper_details_page], position="hidden")

pg.run()
