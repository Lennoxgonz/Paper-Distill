import streamlit as st
import arxiv

# Initialize arxiv client
client = arxiv.Client()

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
        except Exception as e:
            st.error(f"Error: {e}")

# Create expander for each paper if papers are in session state
if st.session_state.papers is not None:
    for i, paper in enumerate(st.session_state.papers):
        with st.container(border=True):
            # Paper title
            st.header(paper.title)

            # Authors section
            authors_text = ", ".join([a.name for a in paper.authors][:3])
            if len(paper.authors) > 3:
                authors_text += " et al."
            st.markdown(f"**Authors:** *{authors_text}*")

            # Paper metadata
            col1, col2, col3 = st.columns([1, 1.5, 0.8])

            with col1:
                st.markdown(
                    f"**Published:** {paper.published.strftime('%Y-%m-%d')}")

            with col2:
                categories = ", ".join(paper.categories)
                st.markdown(f"**Categories:** {categories}")

            # View more button linking to paper details page and clearing cache if other papers were viewed
            # This is to prevent summarys from other papers showing on the selected paper
            with col3:
                if st.button("View Details", key=f"view_{i}", use_container_width=True):
                    st.session_state.abstract_summary = None
                    st.session_state.paper_summary = None
                    show_paper_details(paper)
st.write("Thank you to arXiv for use of its open access interoperability.")
