"""
EMBEDDINGS MODULE
================
This module handles the creation of embeddings for clinical case data.
It uses Sentence Transformers to convert text into vector representations.

Why Embeddings?
- Convert text into numerical vectors that capture semantic meaning
- Similar texts will have similar vector representations
- Enables similarity search in the vector database
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


class EmbeddingGenerator:
    """
    Generate embeddings using Sentence Transformers.
    
    This class wraps the SentenceTransformer model and provides methods
    to generate embeddings for individual texts or batches of texts.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the Sentence Transformer model to use.
                       "all-MiniLM-L6-v2" is lightweight and efficient for most use cases.
        """
        print(f"[INFO] Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"[INFO] Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts at once.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts or not all(isinstance(t, str) for t in texts):
            raise ValueError("texts must be a non-empty list of strings")
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Dimension as integer
        """
        return self.model.get_sentence_embedding_dimension()


# Helper function for quick embedding generation
def embed_text(text: str, generator: EmbeddingGenerator = None) -> np.ndarray:
    """
    Quick function to embed text.
    Creates a generator if one is not provided (slower but convenient).
    
    Args:
        text: Text to embed
        generator: Optional EmbeddingGenerator instance for reuse
        
    Returns:
        Embedding vector
    """
    if generator is None:
        generator = EmbeddingGenerator()
    
    return generator.generate_embedding(text)
