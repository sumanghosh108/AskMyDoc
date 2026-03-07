### RAG Application
'''
    Production grade Retrival augmented generation(RAG)
'''
# what is building?
--domain specific ask my document system.
--You pick a corpus of documents, it could be tachnical document, research paper, legeal contract, health care document.
--build a system that retrives informations , answers questions with proper citations.
--
## phase 1: Fundamental working
-- injest documents(pdf, markdown or web pages)
-- chunk them into piceses  about 500 to 800 tokens
-- with roughly 100 tokens of overlap between chunks
-- than store those chunks as embeddings in a vector store(chromaDB)
-- then build retrival pipeline that pulls the top k most relevant chunks for a given query
-- generates a answer that cites where the information came from

## phase 2: production-quality
-- impliment a hybrid retrival(combing traditional BM25 keyword search with vector base semantic search)
-- at top of that add a cross encoder re-ranker
-- which takes your initial set retrive chunks and rescore them using model that evaluate the query and each chunk together as a pair
---> store all prompts in versioned config files
## phase 3: measurement of faithfulness
-- you going to curate a golden evaluation dataset of 100 to 200 question-answer pairs
-- that manually verify for correctness
-- you write a offline evaluation scripts that measure faithfullness which essentailly asked the questions and the claim they generate answer actually supported by the retrived chunks
-- for each question you will have a ground truth answer and a list of source chunks that support it
---> if quality drops below your threshold, the build failds

## Tech stack
-- Orchestration: LanghChain/LangGraph
-- Vector Store: ChromaDB
-- Reranking: Cohere reranker
-- Evaluation: ragas


