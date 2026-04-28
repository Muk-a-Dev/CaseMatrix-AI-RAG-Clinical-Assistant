"""
RAG PIPELINE MODULE
===================
This module implements the Retrieval-Augmented Generation (RAG) pipeline.

How RAG Works:
1. User submits a clinical query
2. Query is converted to embedding
3. Similarity search finds most relevant cases in vector DB
4. Retrieved cases provide context
5. LLM generates response grounded in retrieved documents

This ensures responses are based on actual case data rather than hallucinations.
"""

import json
import chromadb
from chromadb.config import Settings
from embeddings import EmbeddingGenerator
from typing import List, Dict, Tuple
import os


class RAGPipeline:
    """
    Complete RAG Pipeline for clinical case retrieval and response generation.
    
    This orchestrates:
    - Loading clinical data
    - Embedding cases
    - Storing in vector database
    - Retrieving similar cases
    - Generating responses based on retrieved context
    """
    
    def __init__(self, 
                 data_path: str = "data/clinical_cases.json",
                 collection_name: str = "clinical_cases",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG pipeline.
        
        Args:
            data_path: Path to clinical cases JSON file
            collection_name: Name for ChromaDB collection
            embedding_model: Sentence Transformer model name
        """
        self.data_path = data_path
        self.collection_name = collection_name
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        
        # Initialize ChromaDB (persistent storage in ./chroma_data)
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_data",
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(settings)
        self.collection = None
        
        print("[INFO] RAG Pipeline initialized")
    
    def load_clinical_data(self) -> List[Dict]:
        """
        Load clinical cases from JSON file.
        
        Returns:
            List of case dictionaries
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        print(f"[INFO] Loaded {len(cases)} clinical cases from {self.data_path}")
        return cases
    
    def create_case_text(self, case: Dict) -> str:
        """
        Create searchable text representation of a case.
        Combines all relevant fields for better semantic search.
        
        Args:
            case: Single case dictionary
            
        Returns:
            Formatted case text
        """
        text_parts = [
            f"Case ID: {case.get('case_id', 'Unknown')}",
            f"Title: {case.get('title', '')}",
            f"Symptoms: {case.get('symptoms', '')}",
            f"Diagnosis: {case.get('diagnosis', '')}",
            f"Treatment: {case.get('treatment', '')}",
        ]
        return " | ".join(text_parts)
    
    def index_clinical_cases(self, force_recreate: bool = False) -> int:
        """
        Load clinical cases and index them in the vector database.
        
        Args:
            force_recreate: If True, recreate collection even if it exists
            
        Returns:
            Number of cases indexed
        """
        # Check if collection already exists and has data
        try:
            if self.collection is None:
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            
            existing_count = self.collection.count()
            
            if existing_count > 0 and not force_recreate:
                print(f"[INFO] Collection '{self.collection_name}' already contains {existing_count} cases")
                return existing_count
        except:
            pass
        
        # Load cases
        cases = self.load_clinical_data()
        
        # Prepare data for indexing
        ids = []
        documents = []
        metadatas = []
        
        for case in cases:
            case_text = self.create_case_text(case)
            
            ids.append(case.get('case_id'))
            documents.append(case_text)
            
            # Store metadata for easy retrieval
            metadata = {
                'title': case.get('title', ''),
                'symptoms': case.get('symptoms', ''),
                'diagnosis': case.get('diagnosis', ''),
                'treatment': case.get('treatment', ''),
                'patient_age': str(case.get('patient_age', '')),
                'gender': case.get('gender', ''),
                'duration_days': str(case.get('duration_days', ''))
            }
            metadatas.append(metadata)
        
        # Add to collection (embeddings are automatically generated)
        print(f"[INFO] Indexing {len(cases)} cases into vector database...")
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"[INFO] Successfully indexed {len(cases)} clinical cases")
        return len(cases)
    
    def retrieve_similar_cases(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Retrieve similar clinical cases for a given query.
        
        Args:
            query: Clinical query or symptom description
            n_results: Number of similar cases to retrieve (default 5)
            
        Returns:
            List of dictionaries containing similar cases with metadata
        """
        if self.collection is None:
            raise RuntimeError("Collection not initialized. Call index_clinical_cases() first.")
        
        print(f"[INFO] Searching for {n_results} similar cases for query: {query[:50]}...")
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        retrieved_cases = []
        
        if results and results['ids'] and len(results['ids']) > 0:
            for i, case_id in enumerate(results['ids'][0]):
                case_data = {
                    'case_id': case_id,
                    'distance': results['distances'][0][i],  # Lower = more similar
                    'similarity_score': round(1 - results['distances'][0][i], 3),  # Convert to similarity (0-1)
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                }
                retrieved_cases.append(case_data)
        
        print(f"[INFO] Retrieved {len(retrieved_cases)} similar cases")
        return retrieved_cases
    
    def generate_response(self, query: str, retrieved_cases: List[Dict]) -> str:
        """
        Generate a response based on retrieved cases.
        
        This is a simple template-based approach. For production, you would integrate
        with an LLM like GPT-4 for more sophisticated generation.
        
        Args:
            query: Original user query
            retrieved_cases: List of retrieved case dictionaries
            
        Returns:
            Generated response string
        """
        if not retrieved_cases:
            return """
            <p><strong>No similar cases found.</strong></p>
            <p>The system could not find clinical cases matching your query in the knowledge base.
            Please try reformulating your question with different symptoms or medical terms.</p>
            """
        
        # Build response from retrieved cases
        response_parts = [
            f"<p><strong>Query:</strong> {query}</p>",
            "<p><strong>Based on {0} similar cases in our database:</strong></p>".format(len(retrieved_cases)),
            "<div style='background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0;'>"
        ]
        
        for i, case in enumerate(retrieved_cases, 1):
            metadata = case.get('metadata', {})
            similarity = case.get('similarity_score', 0)
            
            case_summary = f"""
            <div style='margin-bottom: 15px; padding: 10px; border-left: 4px solid #007bff;'>
                <p><strong>Case {i}: {metadata.get('title', 'Unknown')} (ID: {case.get('case_id')})</strong></p>
                <p><em>Similarity Score: {similarity * 100:.1f}%</em></p>
                <p><strong>Symptoms:</strong> {metadata.get('symptoms', 'Not specified')}</p>
                <p><strong>Diagnosis:</strong> {metadata.get('diagnosis', 'Not specified')}</p>
                <p><strong>Treatment:</strong> {metadata.get('treatment', 'Not specified')}</p>
            </div>
            """
            response_parts.append(case_summary)
        
        response_parts.append("</div>")
        
        # Add recommendation
        response_parts.append("""
        <p><em><strong>Note:</strong> These results are retrieved from similar cases in the clinical database.
        This is for educational purposes and training. Always consult with qualified healthcare professionals
        for actual patient care and diagnosis.</em></p>
        """)
        
        return "\n".join(response_parts)
    
    def process_query(self, query: str, n_results: int = 5) -> Dict:
        """
        Complete RAG pipeline: retrieve cases and generate response.
        
        Args:
            query: User's clinical query
            n_results: Number of similar cases to retrieve
            
        Returns:
            Dictionary with query, retrieved cases, and generated response
        """
        # Retrieve similar cases
        retrieved_cases = self.retrieve_similar_cases(query, n_results)
        
        # Generate response
        response = self.generate_response(query, retrieved_cases)
        
        return {
            'query': query,
            'retrieved_cases': retrieved_cases,
            'response': response,
            'num_results': len(retrieved_cases)
        }


# Singleton instance for app usage
_rag_instance = None

def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create the RAG pipeline singleton.
    Ensures only one instance is used throughout the application.
    
    Returns:
        RAGPipeline instance
    """
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGPipeline()
        _rag_instance.index_clinical_cases()
    return _rag_instance
