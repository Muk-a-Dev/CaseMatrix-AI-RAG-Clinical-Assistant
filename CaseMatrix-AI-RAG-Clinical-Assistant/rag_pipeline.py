"""TF-IDF retrieval pipeline based on Kaggle CSV dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RAGPipeline:
    def __init__(self, data_path: str | None = None):
        project_root = Path(__file__).resolve().parent
        self.data_path = Path(data_path) if data_path else project_root / "data" / "dataset.csv"
        if not self.data_path.exists():
            fallback = project_root / "backend" / "data" / "dataset.csv"
            if fallback.exists():
                self.data_path = fallback

        self.cases = self.load_clinical_data()
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.case_texts = [self.create_case_text(case) for case in self.cases]
        self.case_matrix = self.vectorizer.fit_transform(self.case_texts) if self.case_texts else None
    
    def load_clinical_data(self) -> List[Dict]:
        """Load clinical cases from Kaggle CSV and normalize into case objects."""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"CSV dataset not found at '{self.data_path}'. Please place dataset.csv in data/."
            )

        df = pd.read_csv(self.data_path)

        disease_col = None
        for col in df.columns:
            if col.strip().lower() == "disease":
                disease_col = col
                break

        if disease_col is None:
            raise ValueError("dataset.csv must contain a 'Disease' column")

        symptom_cols = [col for col in df.columns if col.strip().lower().startswith("symptom_")]
        if not symptom_cols:
            raise ValueError("dataset.csv must contain Symptom_1, Symptom_2, ... columns")

        cases: List[Dict] = []
        for idx, row in df.iterrows():
            disease_val = row.get(disease_col, "")
            diagnosis = "" if pd.isna(disease_val) else str(disease_val).strip()
            if not diagnosis:
                continue

            symptoms: List[str] = []
            for col in symptom_cols:
                value = row.get(col, "")
                if pd.isna(value):
                    continue
                cleaned = str(value).replace("_", " ").strip().strip(",")
                if cleaned:
                    symptoms.append(cleaned)

            if not symptoms:
                continue

            symptom_text = ", ".join(symptoms)
            cases.append(
                {
                    "case_id": str(idx),
                    "title": diagnosis,
                    "symptoms": symptom_text,
                    "symptoms_list": symptoms,
                    "diagnosis": diagnosis,
                    "treatment": "Consult a qualified clinician for evaluation and management; this tool is for study only.",
                    "patient_age": "",
                    "gender": "",
                    "duration_days": "",
                }
            )

        return cases
    
    def create_case_text(self, case: Dict) -> str:
        """Build a searchable text string for one case."""
        text_parts = [
            f"Case ID: {case.get('case_id', 'Unknown')}",
            f"Condition: {case.get('title', '')}",
            f"Disease label: {case.get('diagnosis', '')}",
            f"Symptoms: {case.get('symptoms', '')}",
            f"Treatment note: {case.get('treatment', '')}",
        ]
        return " | ".join(text_parts)
    
    def index_clinical_cases(self, force_recreate: bool = False) -> int:
        """Reload CSV data and rebuild TF-IDF vectors."""
        self.cases = self.load_clinical_data()
        self.case_texts = [self.create_case_text(case) for case in self.cases]
        self.case_matrix = self.vectorizer.fit_transform(self.case_texts) if self.case_texts else None
        return len(self.cases)
    
    def retrieve_similar_cases(self, query: str, n_results: int = 5) -> List[Dict]:
        """Return top-N similar cases using cosine similarity over TF-IDF vectors."""
        if self.case_matrix is None or not self.cases:
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.case_matrix).flatten()
        ranked_indexes = np.argsort(similarities)[::-1][:n_results]

        retrieved_cases: List[Dict] = []
        for index in ranked_indexes:
            case = self.cases[index]
            retrieved_cases.append(
                {
                    "case_id": case.get("case_id", "Unknown"),
                    "similarity_score": round(float(similarities[index]), 3),
                    "metadata": {
                        "title": case.get("title", ""),
                        "symptoms": case.get("symptoms", ""),
                        "symptoms_list": list(case.get("symptoms_list") or []),
                        "diagnosis": case.get("diagnosis", ""),
                        "treatment": case.get("treatment", ""),
                        "patient_age": str(case.get("patient_age", "")),
                        "gender": case.get("gender", ""),
                        "duration_days": str(case.get("duration_days", "")),
                    },
                }
            )

        return retrieved_cases
    
    def generate_response(self, query: str, retrieved_cases: List[Dict]) -> str:
        """Create a structured text summary from retrieved cases (educational use)."""
        if not retrieved_cases:
            return (
                "No indexed rows were returned for this query. "
                "Try adding more symptom or disease keywords that appear in your dataset (e.g. GERD, chest pain, acidity)."
            )

        lines: List[str] = []
        lines.append("=== CaseMatrix AI — retrieval summary ===")
        lines.append("")
        lines.append(f"Your query: {query}")
        lines.append(
            f"Showing {len(retrieved_cases)} row(s) from the library, ranked by TF‑IDF cosine similarity "
            "(word overlap between your text and each row's condition + symptom fields)."
        )
        scores = [float(c.get("similarity_score") or 0) for c in retrieved_cases]
        if scores and max(scores) < 0.12:
            lines.append(
                "Heads-up: scores are low—your wording may not overlap strongly with dataset tokens. "
                "Try synonyms from the dataset (e.g. stomach_pain vs abdominal pain, or disease names like GERD)."
            )
        lines.append("")
        lines.append("--- Ranked matches (highest first) ---")
        lines.append("")

        for index, case in enumerate(retrieved_cases, start=1):
            metadata = case.get("metadata", {})
            title = metadata.get("title") or metadata.get("diagnosis") or "Unknown condition"
            diag = metadata.get("diagnosis") or title
            score = float(case.get("similarity_score") or 0)
            lines.append(f"[{index}] {title}")
            lines.append(f"    Row ID: {case.get('case_id', '—')}  |  Similarity: {score:.3f} (0–1 scale)")
            lines.append(f"    Condition / disease label: {diag}")
            sym_line = metadata.get("symptoms") or "Not specified"
            lines.append(f"    Symptoms (concatenated from CSV): {sym_line}")
            lines.append(f"    Guidance: {metadata.get('treatment', 'Not specified')}")
            lines.append("")

        lines.append("--- End of matches ---")
        lines.append(
            "Educational use only: not a diagnosis. If you searched for GERD or any complaint, "
            "verify against curricula and clinicians; this output only reflects dataset text similarity."
        )
        return "\n".join(lines)
    
    def process_query(self, query: str, n_results: int = 5) -> Dict:
        """Retrieve cases and generate a simple answer payload."""
        top_cases = self.retrieve_similar_cases(query, n_results)
        answer = self.generate_response(query, top_cases)

        return {"query": query, "cases": top_cases, "answer": answer, "num_results": len(top_cases)}


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
    return _rag_instance
