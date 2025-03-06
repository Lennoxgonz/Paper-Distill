import streamlit as st
import arxiv
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

# Initialize arxiv client
client = arxiv.Client()

# Fetch papers from arxiv
def fetch_papers(query, categories, max_results=10):
    # Add categories to query if there are any
    if categories:
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        query = f"{query} AND ({cat_query})" if query else cat_query

    # Perform API call and cache in session state
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = list(client.results(search))
    st.session_state.papers = results

    return results

def show_paper_details(paper):
    st.session_state.selected_paper = paper
    st.switch_page("paper_details_page.py")

# Sidebar how it works section
st.sidebar.title("How it works")

with st.sidebar.expander("**Abstract Summarization**"):
    st.write(
        """Creates a summarized version of the paper's abstract using the 
        facebook/bart-large-cnn model. This is a BART (Bidirectional and Auto-Regressive Transformers) 
        based model which was fine-tuned on the CNN/Daily Mail dataset of news articles and their summaries."""
    )

# Search interface and title
st.title("Science Stratified")
st.write("Search for papers with ML-enhanced summaries")

search_query = st.text_input("Search", placeholder="Enter keywords")
categories = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "physics", "math", "q-bio"]
selected_cats = st.multiselect("Categories", categories)

# Handle search button click
if st.button("Search"):
    with st.spinner("Searching for papers..."):
        try:
            papers = fetch_papers(search_query, selected_cats)

            if not papers:
                st.warning("No papers found. Try different search terms.")
            else:
                st.success(f"Found {len(papers)} papers")
        except Exception as e:
            st.error(f"Error: {e}")

# Create expander for each paper if papers are in session state
if st.session_state.papers is not None:
    for i, paper in enumerate(st.session_state.papers):
        with st.container():
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
                if st.button("View More", key=f"view_more_{i}"):
                    show_paper_details(paper)
            st.markdown(
                f"**Links:** [PDF]({paper.pdf_url}) | [arXiv]({paper.entry_id})"
            )

st.write("Thank you to arXiv for use of its open access interoperability.")
