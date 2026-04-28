# CaseMatrix — Clinical RAG Assistant

Author(s): Your Name
Affiliation: Your Affiliation
Date: 28 April 2026

---

## Abstract

This document is the comprehensive project report for CaseMatrix, a Retrieval-Augmented Generation (RAG) clinical assistant designed to retrieve and synthesize clinical case information from a curated dataset and present concise, clinically relevant responses. The report covers motivation, background, system architecture, data sources, methods (embeddings, indexing, retrieval, generation), implementation details, experiments and qualitative results, limitations, ethical considerations, and instructions for reproducing the work.

## Executive Summary

CaseMatrix implements a reproducible RAG pipeline combining vector embeddings, a fast similarity index, and a language model generator to help clinicians explore and reason about clinical cases. The system ingests a curated clinical dataset, builds dense embeddings (see `embeddings.py` and `backend/embeddings.py`), stores vectors in a local index, and serves a web UI (`templates/index.html`) for interactive querying. This report includes run instructions, evaluation examples, and recommendations for deployment and future improvements.

## Table of Contents

- Abstract
- Executive Summary
- 1. Introduction
- 2. Related Work / Background
- 3. System Overview
- 4. Data
- 5. Methods / Pipeline
- 6. Implementation
- 7. Experiments & Results
- 8. Discussion
- 9. Conclusions & Future Work
- References
- Appendix A: Reproducibility & Run Instructions
- Appendix B: Key Code Pointers and File Map

---

## 1. Introduction

Problem statement: Clinicians often need concise, context-aware summaries and comparisons for clinical cases. CaseMatrix aims to accelerate access to case-relevant knowledge using a small curated dataset and a RAG approach to produce accurate, explainable answers.

Objectives:
- Build a pipeline that indexes clinical cases and supports semantic search using embeddings.
- Provide an interface for clinicians to ask questions and receive evidence-backed answers.
- Make the system reproducible and well-documented.

Scope and constraints:
- Prototype-level system using local embeddings and a hosted language model (or local LLM if available).
- Uses curated clinical dataset `data/clinical_cases.json` and `data/dataset.csv`.
- Not intended to provide autonomous clinical decisions — only informational assistance.

Clinical relevance:
- Use-cases include study preparation, clinical teaching, exam prep, and quick case summarization.

## 2. Related Work / Background

- Retrieval-Augmented Generation (RAG) leverages retrieval (vector or sparse) to provide context to a generative model.
- Prior systems: semantic search tools for clinical notes, biomedical retrieval systems, and clinical decision support prototypes.
- Key references: DPR, RAG (FAIR), OpenAI retrieval examples, Semantic Scholar papers on clinical embeddings.

## 3. System Overview

High-level components:
- Data ingestion and preprocessing (scripts operate on `data/clinical_cases.json`).
- Embedding generation (`embeddings.py`, `backend/embeddings.py`).
- Vector index storage and nearest-neighbor lookup (`rag_pipeline.py`, `backend/rag_pipeline.py`).
- API / backend server (`app.py`, `backend/app.py`).
- Frontend demo (`templates/index.html`, `static/script.js`, `static/style.css`).

Deployment context: The system can be run locally for demo or packaged into a container for deployment. See `ARCHITECTURE.md` for an architecture-level diagram and notes.

Diagram: Recreate or include the diagram from [ARCHITECTURE.md](ARCHITECTURE.md).

User stories:
- "As a student, I want to search for cases with similar presentations." 
- "As an educator, I want example reasoning steps for a given case." 

## 4. Data

Data sources:
- Primary dataset: [data/clinical_cases.json](data/clinical_cases.json)
- Supplementary CSV: [data/dataset.csv](data/dataset.csv)

Data description and schema:
- Each clinical case contains fields like `case_id`, `presentation`, `history`, `exams`, `diagnosis`, `discussion`, and `references` (see `data/clinical_cases.json`).

Preprocessing steps:
- Normalize text (lowercasing optional), remove PII (if present), split long cases into chunks for embedding.
- Token limits: ensure chunks fit model context windows used for embedding and generation.

Privacy & ethics:
- If dataset contains PHI, redact or synthesize patient identifiers.
- Note in report whether data is synthetic or de-identified.

## 5. Methods / Pipeline

Overview:
1. Text chunking: split long case texts into manageable passages.
2. Embedding: compute vector representations using a chosen encoder (e.g., OpenAI embeddings, sentence-transformers, or a local encoder). See `embeddings.py` for implementation details.
3. Indexing: store vectors in an efficient index (FAISS, Annoy, or simpler in-memory KD-tree). `rag_pipeline.py` demonstrates the retrieval flow.
4. Retrieval: perform k-NN lookup for top-k similar passages.
5. RAG: construct prompt including retrieved passages and question, send to a generative model for final answer.
6. Post-processing: sanitize outputs, add citations to retrieved passages.

Algorithms and hyperparameters:
- Embedding model: specify model name and dimension (e.g., `text-embedding-3-small`, SBERT variants).
- k (top-k retrieved passages): 3-10 recommended; tuned for recall/conciseness tradeoff.
- Similarity metric: cosine similarity.
- Chunk size: 200–500 tokens (model-dependent).

Pseudocode (in brief):

1. load index
2. embed(question)
3. results = index.search(vector, top_k)
4. context = join(results.documents)
5. prompt = build_prompt(context, question)
6. answer = LLM.generate(prompt)
7. return {answer, sources: results.metadata}

## 6. Implementation

Tech stack:
- Language: Python 3.9+
- Web: Flask (or FastAPI) for backend; simple HTML/JS for frontend demo
- Embeddings: OpenAI / sentence-transformers
- Index: FAISS (recommended) or in-memory fallback

Key files (location links):
- [app.py](app.py) — top-level demo runner
- [rag_pipeline.py](rag_pipeline.py) — pipeline orchestration
- [embeddings.py](embeddings.py) — embedding utilities
- [backend/app.py](backend/app.py) — backend server for API
- [backend/rag_pipeline.py](backend/rag_pipeline.py) — backend pipeline
- [backend/embeddings.py](backend/embeddings.py)
- Frontend: [templates/index.html](templates/index.html), [static/script.js](static/script.js), [static/style.css](static/style.css)

Runtime and environment:
- See `requirements.txt` for pip dependencies. Record exact versions for reproducibility.

Run instructions (example):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
# or
python backend/app.py
```

Configuration and secrets:
- Document environment variables (API keys for embedding/generation if using external providers). Do not commit secrets to repo.

## 7. Experiments & Results

Evaluation strategy:
- Quantitative metrics depend on task: for retrieval, measure recall@k; for generated answers, evaluate against human judgments or BLEU/ROUGE where applicable.
- For this prototype use qualitative case studies and representative example queries.

Example queries and sample outputs (select a few from `data/clinical_cases.json`):

- Query: "A 65-year-old with progressive dyspnea and bibasilar crackles — what differential diagnoses should I consider?"
- Retrieved evidence: [case_id: 2021-07-01-01] (include short excerpt)
- Generated answer: (Provide a 3–4 sentence synthesized answer with citations to retrieved case excerpts.)

(Include 4–6 such examples showing retrieval snippets and final answers.)

Screenshots:
- Capture UI screenshots from [templates/index.html](templates/index.html) showing query and response.

Tables & plots:
- Provide a small table for retrieval recall or sample counts per diagnosis. Example:

| Metric | Value |
|---|---:|
| Number of cases | N |
| Avg passages per case | M |

## 8. Discussion

Strengths:
- Combines semantic retrieval with generation for context-grounded answers.
- Flexible to swap embedding or LLM providers.

Limitations:
- Small dataset limits generalizability.
- Potential hallucinations from LLMs — mitigation required (source citation, conservative prompts).
- Biases: dataset composition may reflect specialty or regional biases.

Clinical risks & mitigation:
- Risk: incorrect clinical guidance. Mitigation: add disclaimers, present evidence and citations, require human-in-the-loop.

## 9. Conclusions & Future Work

Summary: CaseMatrix demonstrates a lightweight RAG pipeline for clinical case retrieval and synthesis and provides a reproducible demo.

Recommended next steps:
- Expand dataset, incorporate structured EHR fields.
- Improve index (FAISS + IVF + HNSW hybrids) and scalability.
- Add evaluation with clinician raters.
- Add unit and integration tests; CI pipeline for reproducibility.

## References

- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", 2020.
- Karpukhin et al., "Dense Passage Retrieval", 2020.
- Documentation for any embedding / LLM APIs used.

---

# Appendix A — Reproducibility & Run Instructions

Environment (example):
- macOS (developed on macOS)
- Python 3.10
- Virtualenv: `.venv`

Install and run (copy to `README_RUN.md` or include as section):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Build index (if needed)
python rag_pipeline.py --build-index
# Start backend
python backend/app.py
# Open demo at http://localhost:5000 (or port specified in backend/app.py)
```

Files to include when packaging deliverables:
- `Final_Report.pdf` (export of this `report.md`)
- `Presentation.pptx` (slide deck)
- `code.zip` (pruned repository with necessary modules)
- `results/` folder containing images and sample output

Appendix: environment variables
- `OPENAI_API_KEY` (if using OpenAI embeddings/LLM)
- `EMBEDDING_MODEL` (model name)
- `LLM_MODEL` (model name for generation)

# Appendix B — Key Code Pointers and File Map

Project root key files:
- [README.md](README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [app.py](app.py)
- [embeddings.py](embeddings.py)
- [rag_pipeline.py](rag_pipeline.py)
- [backend/app.py](backend/app.py)
- [backend/rag_pipeline.py](backend/rag_pipeline.py)
- [data/clinical_cases.json](data/clinical_cases.json)
- [templates/index.html](templates/index.html)

Contact / Maintainer:
- Name: Your Name
- Email: your.email@example.com

---

Notes & TODOs to finish the report for distribution
- Replace placeholders (N, M, example outputs) with real numbers and captured screenshots.
- Add actual figures (architecture diagram PNG, UI screenshots) into `results/` and reference them here.
- Export to PDF (`Final_Report.pdf`) using pandoc or Word/LaTeX.



