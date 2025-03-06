import streamlit as st

def summarize_abstract(abstract, max_length=100):
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

paper = st.session_state.selected_paper
tabs = st.tabs(["Abstract", "Abstract Summary"])
with tabs[0]:
    st.markdown(paper.summary)
# Abstract summary tab
with tabs[1]:
    summary_key = f"summary_{hash(paper.entry_id)}"
    
    # Render button only if summary has not been generated
    if summary_key not in st.session_state:
        # On button click generate summary and store in session state
        if st.button("Generate Summary"):
            try:
                with st.spinner("Generating summary..."):
                    st.session_state[summary_key] = summarize_abstract(
                        paper.summary)
            except Exception as e:
                st.error(f"Error generating summary: {e}")
    
    # Display summary
    if summary_key in st.session_state:
        st.markdown(f"*{st.session_state[summary_key]}*")