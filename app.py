import streamlit as st
import arxiv
import torch
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

# Download nltk data (if needed)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

client = arxiv.Client()


def fetch_papers(query, categories, max_results=10):
    # Add categories to query if there is any
    if categories:
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        query = f"{query} AND ({cat_query})" if query else cat_query

    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = list(client.results(search))

    return results


# Load model from hugging face


@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_abstract(abstract, max_length=100):
    summarizer = load_summarizer()

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


# Search interface
st.title("Science Stratified")
st.write("Search for papers with ML-enhanced summaries")

search_query = st.text_input("Search", placeholder="Enter keywords")
categories = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "physics", "math", "q-bio"]
selected_cats = st.multiselect("Categories", categories)

# Sidebar
st.sidebar.title("ML Features")
enable_summarization = st.sidebar.checkbox(
    "Enable Abstract Summarization", value=True)
# How it works section in sidebar
with st.sidebar.expander("**How it works**"):
    st.write(
        """**Abstract Summarization** \n\n Creates a summarized version of the paper's abstract using the 
        facebook/bart-large-cnn model. This is a BART (Bidirectional and Auto-Regressive Transformers) 
        based model which was fine-tuned on the CNN/Daily Mail dataset of news articles and their summaries."""
    )
# Handle search button click
if st.button("Search"):
    with st.spinner("Searching for papers..."):
        try:
            papers = fetch_papers(search_query, selected_cats)

            # Store papers in session state for persistence
            st.session_state.papers = papers

            if not papers:
                st.warning("No papers found. Try different search terms.")
            else:
                st.success(f"Found {len(papers)} papers")
        except Exception as e:
            st.error(f"Error: {e}")
            query_str = search_query
            if selected_cats:
                cat_query = " OR ".join(
                    [f"cat:{cat}" for cat in selected_cats])
                query_str = (
                    f"{search_query} AND ({cat_query})" if search_query else cat_query
                )
            st.error(f"Query used: {query_str}")

# Display results if we have papers (either from this search or a previous one)
if "papers" in st.session_state and st.session_state.papers:
    papers = st.session_state.papers

    # Create expander for each paper
    for paper in papers:
        with st.expander(paper.title):

            # Basic paper info
            st.header(paper.title)
            st.markdown(
                f"**Authors:** *{', '.join([a.name for a in paper.authors][:3])}*"
            )
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"**Published:** {paper.published.strftime('%Y-%m-%d')}")
            with col2:
                st.markdown(f"**Categories:** {', '.join(paper.categories)}")
            st.markdown(
                f"**Links:** [PDF]({paper.pdf_url}) | [arXiv]({paper.entry_id})"
            )

            # Abstract/Summary section
            st.markdown("---")
            st.subheader("Abstract")

            # Create separate tab if summarization is enabled
            if enable_summarization:
                abstract_tabs = st.tabs(["AI Summary", "Full Abstract"])

                with abstract_tabs[0]:
                    try:
                        # Use session state to cache summary
                        summary_key = f"summary_{hash(paper.entry_id)}"
                        if summary_key not in st.session_state:
                            with st.spinner("Generating summary..."):
                                st.session_state[summary_key] = summarize_abstract(
                                    paper.summary
                                )

                        summary = st.session_state[summary_key]
                        st.markdown(f"*{summary}*")
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
                        st.markdown(paper.summary)

                with abstract_tabs[1]:
                    st.markdown(paper.summary)
            else:
                st.markdown(paper.summary)
