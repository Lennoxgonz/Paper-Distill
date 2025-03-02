import streamlit as st
import arxiv

client = arxiv.Client()

# Simple search interface
st.title("Science Stratified")
search_query = st.text_input("Search", placeholder="Enter keywords")
categories = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "physics", "math", "q-bio"]
selected_cats = st.multiselect("Categories", categories)

if st.button("Search"):
    query = search_query
    if selected_cats:
        cat_query = " OR ".join([f"cat:{cat}" for cat in selected_cats])
        query = f"{search_query} AND ({cat_query})" if search_query else cat_query
   
    # Execute search
    search = arxiv.Search(query=query, max_results=8, sort_by=arxiv.SortCriterion.SubmittedDate)
   
    try:
        # Display results with expanders instead of buttons
        results = list(client.results(search))
        if not results:
            st.warning("No papers found. Try different search terms.")
        
        for i, paper in enumerate(results):
            with st.expander(f"{paper.title}"):
                st.markdown(f"**Authors:** *{', '.join([a.name for a in paper.authors][:3])}*")
                st.markdown(f"**Abstract:** {paper.summary}")
                st.markdown(f"**Links:** [PDF]({paper.pdf_url}) | [arXiv]({paper.entry_id})")
                st.markdown(f"**Published:** {paper.published.strftime('%Y-%m-%d')}")
                st.markdown(f"**Categories:** {', '.join(paper.categories)}")
            
            # Add some spacing between results
            st.markdown("---")
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.error(f"Query used: {query}")