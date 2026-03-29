import arxiv
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_arxiv_client() -> arxiv.Client:
    return arxiv.Client(
        page_size=50,
        delay_seconds=3.5,
        num_retries=5,
    )


def get_paper_by_id(arxiv_id: str):
    search = arxiv.Search(id_list=[arxiv_id], max_results=1)
    return next(get_arxiv_client().results(search), None)
