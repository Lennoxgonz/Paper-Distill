# Paper Distill
Search for scientific papers and get customized summarization and the ability to ask questions about the paper.

## Features

### Paper Search
The paper search uses the arXiv API to search for papers based on a search query and selected categories. "arXiv is a free distribution service and an open-access archive for nearly 2.4 million scholarly articles in the fields of physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics."

[Learn more about arXiv](https://info.arxiv.org/about/index.html)

### Abstract Summary
The abstract summary feature created a summarized version of the paper's abstract using a locally run instance of the `sshleifer/distilbart-cnn-12-6` model. This is a distilled version of the `facebook/bart-large-cnn` model. A BART based model which was fine-tuned on the CNN/Daily Mail dataset of news articles and their summaries.

The full abstract is passed into the model along with the desired summary length.

Distillation is a technique used to reduce the size of a model and subsequently the required compute power while maintaining most of its performance.

BART (Bidirectional and Auto-Regressive Transformers) architecture was developed by Facebook/Meta. It is particularly effective for text summarization tasks as bidirectional encoding and autoregressive decoding work together to understand the context of the text and generate coherent summaries.

[Learn more about arXiv](https://arxiv.org/abs/1910.13461v1)

### Paper Summary
The paper summary feature summarizes the entire paper based on two user selected parameters, length and technical complexity. The summary is created using Gemini 2.0, a Large Language Model developed by Google that is accessible through the Gemini Developer API.

The paper is downloaded as a pdf, then converted into markdown text, then passed into the model along with a prompt instructing the model to summarize the paper into a certain number of paragraphs at a certain technical complexity.

An API is used here rather than a model run locally like in the abstract summary feature due to the fact that academic papers can be quite long and to summarize one requires a model that can maintain coherence across thousands of tokens. Models like this end up being very large and can be impractical to run locally.

Gemini AI architecture excels at processing long-context tasks through specialized attention mechanisms that maintain understanding across thousands of tokens, while innovations like sliding window attention enable efficient referencing of earlier information, making it powerful for analyzing lengthy documents and complex content.

[Learn more about Gemini 2.0](https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/#gemini-2-0)

[Read the Gemini 1.5 paper](https://arxiv.org/abs/2403.05530v5)

### Ask Questions
The ask questions feature allows users to ask questions about the paper. This is achieved through the use of Gemini 2.0 through the Gemini developer API and works in a very similar way to the paper summary feature.

The paper is downloaded as a pdf, converted to markdown, then passed into the model along with the question to be asked and a prompt instructing the model to answer the question based on the context of the paper.

[Learn more about Gemini 2.0](https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/#gemini-2-0)

[Read the Gemini 1.5 paper](https://arxiv.org/abs/2403.05530v5)