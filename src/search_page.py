import streamlit as st
import arxiv
from arxiv_client import get_arxiv_client
from categories import categories_dict


def fetch_papers(query, categories, max_results=10):
    """Fetch papers from arXiv using a shared, throttled client."""
    if categories:
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        query = f"{query} AND ({cat_query})" if query else cat_query

    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )
    client = get_arxiv_client()
    results = list(client.results(search))
    st.session_state.papers = results

    return results

def show_paper_details(paper):
    st.session_state.selected_paper_id = paper.get_short_id()
    st.switch_page("paper_details_page.py")

st.title("Paper Distill")
st.write("Search for scientific papers and get customized summarization and the ability to ask questions about the paper.")

with st.form("search_form"):
    search_query = st.text_input("Search", placeholder="Enter keywords")
    selected_display_names = st.multiselect("Categories", list(categories_dict.values()))
    submitted = st.form_submit_button("Search")

if submitted:
    selected_cats = []
    for display_name in selected_display_names:
        for code, name in categories_dict.items():
            if name == display_name:
                selected_cats.append(code)
                break

    with st.spinner("Searching for papers..."):
        try:
            papers = fetch_papers(search_query, selected_cats)

            if not papers:
                st.warning("No papers found. Try different search terms.")
        except Exception as e:
            st.error(f"Error: {e}")

# Create expander for each paper if results are returned
if st.session_state.papers is not None:
    for i, paper in enumerate(st.session_state.papers):
        with st.container(border=True):
            st.header(paper.title)

            authors_text = ", ".join([a.name for a in paper.authors][:3])
            if len(paper.authors) > 3:
                authors_text += " et al."
            st.markdown(f"**Authors:** *{authors_text}*")

            col1, col2, col3 = st.columns([1, 1.5, 0.8])

            with col1:
                st.markdown(
                    f"**Published:** {paper.published.strftime('%Y-%m-%d')}")

            with col2:
                display_categories = [categories_dict.get(cat, cat) for cat in paper.categories]
                categories_display = ", ".join(display_categories)
                st.markdown(f"**Categories:** {categories_display}")

            with col3:
                if st.button("View Details", key=f"view_{i}", use_container_width=True):
                    st.session_state.abstract_summary = None
                    st.session_state.paper_summary = None
                    show_paper_details(paper)

st.write("Thank you to arXiv for use of its open access interoperability.")
