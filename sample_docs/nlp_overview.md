# Natural Language Processing (NLP)

Natural Language Processing is a field at the intersection of computer science, artificial intelligence, and linguistics. Its primary goal is to enable computers to understand, interpret, and generate human language in a meaningful way.

## Core NLP Tasks

### Text Classification
Text classification assigns predefined categories to text documents. Applications include spam detection, sentiment analysis, and topic categorization. Common approaches include bag-of-words models, TF-IDF with classic classifiers, and modern transformer-based models like BERT.

### Named Entity Recognition (NER)
NER identifies and classifies named entities in text into predefined categories such as person names, organizations, locations, dates, and quantities. This is essential for information extraction from unstructured text.

### Machine Translation
Machine translation automatically translates text from one language to another. Modern neural machine translation systems use encoder-decoder architectures with attention mechanisms, achieving near-human quality for many language pairs.

### Text Summarization
Text summarization creates concise summaries of longer documents. There are two main approaches:
- **Extractive summarization**: Selects and concatenates the most important sentences from the source text
- **Abstractive summarization**: Generates new sentences that capture the essence of the source text

## Transformer Architecture

The transformer architecture, introduced in the paper "Attention Is All You Need" (2017), has become the foundation of modern NLP. Key components include:

### Self-Attention Mechanism
Self-attention allows each position in the sequence to attend to all other positions. This enables the model to capture long-range dependencies more effectively than RNNs.

The attention computation follows:
- **Query (Q)**, **Key (K)**, **Value (V)** matrices are computed from input embeddings
- Attention weights are computed as softmax(QK^T / √d_k)
- Output is the weighted sum of values

### Multi-Head Attention
Multiple attention heads allow the model to jointly attend to information from different representation subspaces. This provides richer representations than single-head attention.

### Positional Encoding
Since transformers process all positions simultaneously (unlike RNNs), positional encodings are added to input embeddings to inject information about token positions in the sequence.

## Large Language Models (LLMs)

Large Language Models are transformer-based models trained on vast amounts of text data. Notable models include:

- **GPT series** (OpenAI): Autoregressive models trained to predict the next token
- **BERT** (Google): Bidirectional model pre-trained with masked language modeling
- **T5** (Google): Text-to-text framework treating all tasks as text generation
- **LLaMA** (Meta): Open-source large language model family
- **Gemini** (Google): Multimodal model capable of processing text, images, and code

### Retrieval-Augmented Generation (RAG)

RAG combines the strengths of information retrieval and text generation. Instead of relying solely on knowledge stored in model parameters, RAG systems:

1. **Retrieve** relevant documents from a knowledge base given a user query
2. **Augment** the input prompt with retrieved context
3. **Generate** an answer grounded in the retrieved information

This approach reduces hallucinations, allows for easy knowledge updates without retraining, and provides source attribution for generated answers.

## Evaluation in NLP

### Intrinsic Metrics
- **Perplexity**: Measures how well a language model predicts text (lower is better)
- **BLEU Score**: Evaluates machine translation quality by comparing to reference translations
- **ROUGE Score**: Measures overlap between generated and reference summaries

### Extrinsic Metrics
- Task-specific accuracy, F1, or other metrics depending on the downstream application
- **Human evaluation**: Gold standard for assessing quality, fluency, and relevance
