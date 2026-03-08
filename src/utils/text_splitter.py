"""
Simple text splitter without heavy dependencies.
Replacement for langchain_text_splitters to avoid PyTorch dependency.
"""

from typing import List


class SimpleTextSplitter:
    """
    Simple recursive character text splitter.
    Splits text into chunks without requiring transformers/torch.
    """
    
    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
        separators: List[str] = None
    ):
        """
        Initialize text splitter.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to split on (in order of preference)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # If text is smaller than chunk size, return as is
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is the last chunk, take everything
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a good split point using separators
            split_point = end
            for separator in self.separators:
                if not separator:
                    continue
                
                # Look for separator near the end of the chunk
                search_start = max(start, end - 100)  # Look back up to 100 chars
                search_text = text[search_start:end + 100]  # Look ahead up to 100 chars
                
                sep_index = search_text.rfind(separator)
                if sep_index != -1:
                    split_point = search_start + sep_index + len(separator)
                    break
            
            # Add chunk
            chunks.append(text[start:split_point].strip())
            
            # Move start position with overlap
            start = split_point - self.chunk_overlap
            if start < 0:
                start = 0
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def create_documents(self, texts: List[str], metadatas: List[dict] = None):
        """
        Create documents from texts (compatible with langchain interface).
        
        Args:
            texts: List of texts to split
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of document dicts with 'page_content' and 'metadata'
        """
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        documents = []
        for text, metadata in zip(texts, metadatas):
            chunks = self.split_text(text)
            for chunk in chunks:
                documents.append({
                    'page_content': chunk,
                    'metadata': metadata.copy()
                })
        
        return documents
