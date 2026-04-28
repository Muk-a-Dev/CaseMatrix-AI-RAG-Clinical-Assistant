# CaseMatrix AI - Architecture & Technical Documentation

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Browser (Chrome/Firefox/Safari)                         │   │
│  │  - React to user input                                   │   │
│  │  - Display search interface                              │   │
│  │  - Show retrieved cases and responses                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/AJAX
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    API LAYER (Flask)                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  app.py - Route Handler                                 │   │
│  │  - GET /          → Serve frontend                      │   │
│  │  - POST /api/search                                     │   │
│  │  - GET /api/cases/stats                                 │   │
│  │  - GET /api/health                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                   RAG PIPELINE LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  rag_pipeline.py                                         │   │
│  │                                                          │   │
│  │  1. Query Embedding                                     │   │
│  │  2. Similarity Search                                   │   │
│  │  3. Result Retrieval                                    │   │
│  │  4. Response Generation                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
    ┌──────────────┐        ┌──────────────────┐
    │ embeddings.py│        │ Vector Database  │
    │              │        │ (ChromaDB)       │
    │ Sentence     │        │                  │
    │ Transformers │        │ - Stores vectors │
    │              │        │ - Similarity idx │
    └──────────────┘        └──────────────────┘
          │                         ▲
          ▼                         │
    ┌──────────────────────────────┐
    │   data/clinical_cases.json   │
    │   (20 anonymized cases)      │
    └──────────────────────────────┘
```

---

## 🔄 Data Flow: Complete Request Lifecycle

```
USER ACTION (Enter query & click Search)
         │
         ▼
┌─────────────────────────────────────────┐
│ Frontend: script.js                     │
│ - Get query from input                  │
│ - Validate input                        │
│ - Show loading spinner                  │
│ - Send AJAX POST to /api/search         │
└─────────────────────────────────────────┘
         │
         │ {"query": "...", "num_results": 5}
         ▼
┌─────────────────────────────────────────┐
│ Backend: app.py - /api/search route     │
│ - Receive JSON request                  │
│ - Validate query parameters             │
│ - Call rag_pipeline.process_query()     │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ RAG Pipeline: process_query()           │
│ 1. Call retrieve_similar_cases(query)   │
│ 2. Call generate_response(query, cases) │
│ 3. Return combined results              │
└─────────────────────────────────────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────────┐      ┌────────────────────────┐
│ retrieve_similar     │      │ generate_response()    │
│ _cases()             │      │                        │
│                      │      │ - Format retrieved     │
│ 1. Embed query       │      │   cases into HTML      │
│ 2. Search ChromaDB   │      │ - Create summary       │
│ 3. Get top N cases   │      │ - Add disclaimers      │
│ 4. Return with scores│      │                        │
└──────────────────────┘      └────────────────────────┘
         │                                 │
         └─────────────────┬───────────────┘
                          │
                          ▼
         ┌──────────────────────────────────┐
         │ app.py - Format Response         │
         │ {                                │
         │   "success": true,               │
         │   "query": "...",                │
         │   "retrieved_cases": [...],      │
         │   "response": "<HTML>...",       │
         │   "num_results": 5               │
         │ }                                │
         └──────────────────────────────────┘
                          │
                          │ JSON Response
                          ▼
         ┌──────────────────────────────────┐
         │ Frontend: script.js               │
         │ - Hide loading spinner           │
         │ - Parse JSON response            │
         │ - Create case card elements      │
         │ - Display results section        │
         │ - Scroll to results              │
         └──────────────────────────────────┘
                          │
                          ▼
         ┌──────────────────────────────────┐
         │ USER SEES: Retrieved cases       │
         │ & generated response             │
         └──────────────────────────────────┘
```

---

## 🧬 Module Responsibilities

### 1. app.py (Flask Backend)

**Purpose**: Main application server handling HTTP requests

**Key Components**:
```python
# Route Handlers
@app.route('/')                 # Serve index.html
@app.route('/api/search', methods=['POST'])  # Main search
@app.route('/api/cases/stats')  # Get statistics
@app.route('/api/cases/list')   # List all cases

# Functions
- search_cases()        # Process user query, call RAG
- health_check()        # Server status
- get_cases_stats()     # Database stats
- list_all_cases()      # Return all cases
```

**Responsibilities**:
- ✓ Receive HTTP requests
- ✓ Validate input
- ✓ Orchestrate RAG pipeline
- ✓ Format and send responses
- ✓ Handle errors gracefully
- ✓ Enable CORS for frontend

---

### 2. rag_pipeline.py (RAG Orchestration)

**Purpose**: Implement Retrieval-Augmented Generation workflow

**Class: RAGPipeline**

```python
def __init__()
    # Initialize embeddings and ChromaDB
    
def load_clinical_data()
    # Load JSON cases → Python objects
    
def create_case_text()
    # Combine case fields into searchable string
    
def index_clinical_cases()
    # Load cases → Create embeddings → Store in ChromaDB
    
def retrieve_similar_cases(query, n_results)
    # Search vector DB for similar cases
    
def generate_response(query, cases)
    # Create HTML response from retrieved cases
    
def process_query(query, n_results)
    # Complete pipeline: retrieve + generate
```

**Key Concepts**:
- **Singleton Pattern**: One RAG instance per app
- **Lazy Loading**: Cases indexed on first access
- **Caching**: Vector DB persists between requests

---

### 3. embeddings.py (Vector Generation)

**Purpose**: Generate embeddings using Sentence Transformers

**Class: EmbeddingGenerator**

```python
def __init__(model_name)
    # Load pre-trained model: "all-MiniLM-L6-v2"
    
def generate_embedding(text)
    # Single text → 384-dimensional vector
    
def generate_embeddings_batch(texts)
    # Multiple texts → Multiple vectors
    
def get_embedding_dimension()
    # Return 384 (vector size)
```

**Why Sentence Transformers?**
- ✅ Lightweight (384 dimensions)
- ✅ Fast inference (<100ms)
- ✅ No external API calls
- ✅ Good semantic understanding
- ✅ Fine-tuned on sentence pairs

---

### 4. index.html (Frontend - Structure)

**Key Sections**:
```html
<nav>                 <!-- Header with title -->
<form>                <!-- Search interface -->
<div#results>         <!-- Results display -->
<div#response>        <!-- AI response -->
<div#cases>           <!-- Case cards -->
<footer>              <!-- Footer info -->
```

---

### 5. static/style.css (Frontend - Styling)

**CSS Organization**:
- Global styles (colors, fonts)
- Component styles (cards, buttons, forms)
- Responsive design (mobile-friendly)
- Animation classes (slide-in effects)

---

### 6. static/script.js (Frontend - Interaction)

**Key Functions**:
```javascript
performSearch()          // Main search handler
displayResults(data)     // Render results
createCaseElement()      // Build case card DOM
showError() / hideError()// Error handling
```

---

## 🔍 Search Algorithm Details

### Vector Similarity Search Process

```
1. USER QUERY
   "Patient with chest pain and shortness of breath"
   
                    ▼
                    
2. EMBEDDING
   Query → SentenceTransformer → [0.23, -0.45, 0.12, ..., 0.88]
                                   (384 dimensions)
                    ▼
                    
3. SIMILARITY CALCULATION
   ChromaDB uses COSINE SIMILARITY:
   
   similarity = (Query_Vector · Case_Vector) / 
                (||Query_Vector|| × ||Case_Vector||)
   
   Result: 0 to 1 (higher = more similar)
   
                    ▼
                    
4. RANKING & RETRIEVAL
   All 20 cases scored:
   - Case 1: 0.87 (87% match) ← Most similar
   - Case 2: 0.76 (76% match)
   - Case 3: 0.72 (72% match)
   - ...
   - Case 20: 0.34 (34% match)
   
   Return top N (default: 5)
                    ▼
                    
5. RETURN RESULTS
   - Case IDs
   - Similarity scores
   - Full case data
   - Metadata
```

---

## 💾 Data Storage Architecture

### ChromaDB Vector Index Structure

```
collection: "clinical_cases"
├── Document Store
│   ├── doc_0: "Case ID: CASE001 | Title: ... | Symptoms: ..."
│   ├── doc_1: "Case ID: CASE002 | Title: ... | Symptoms: ..."
│   └── ...
│
├── Vector Index (HNSW - Hierarchical Navigable Small World)
│   ├── vector_0: [0.23, -0.45, 0.12, ..., 0.88] (384-dim)
│   ├── vector_1: [0.15, -0.52, 0.09, ..., 0.91] (384-dim)
│   └── ...
│
├── Metadata Store
│   ├── meta_0: {"title": "...", "symptoms": "...", ...}
│   ├── meta_1: {"title": "...", "symptoms": "...", ...}
│   └── ...
│
└── ID Mapping
    ├── "CASE001" → index 0
    ├── "CASE002" → index 1
    └── ...
```

### File System Layout

```
project/
├── chroma_data/              ← Vector DB storage (created on first run)
│   ├── index/
│   │   └── index_metadata.parquet
│   ├── chroma/
│   │   ├── clinical_cases/   ← Our collection
│   │   │   ├── data/
│   │   │   │   ├── embeddings_0.bin
│   │   │   │   ├── document_store.parquet
│   │   │   │   └── ...
│   │   │   └── state.json
│   │   └── ...
│   └── ...
│
├── data/
│   └── clinical_cases.json   ← Source data
│
└── ...
```

---

## 🔐 Security Considerations

### Input Validation
```python
# Check query not empty
if not query:
    return error("Empty query")

# Check query length
if len(query) > 1000:
    return error("Query too long")

# Check num_results valid
if num_results < 1 or num_results > 10:
    num_results = 5
```

### Error Handling
```python
try:
    result = rag_pipeline.process_query(query, num_results)
    return jsonify(result), 200
except Exception as e:
    log_error(e)
    return jsonify({"error": str(e)}), 500
```

### CORS Protection
```python
CORS(app)  # Allow frontend to call backend
```

---

## ⚡ Performance Optimization

### Optimization Techniques

1. **Lazy Loading**
   - ChromaDB index created only when needed
   - Cases indexed once, reused across requests

2. **Batch Processing**
   - Embeddings generated in batch during indexing
   - Reduces redundant computation

3. **Efficient Model**
   - MiniLM (384-dim) vs BERT (768-dim)
   - 50% smaller, 2x faster, similar quality

4. **Vector Index**
   - HNSW (Hierarchical Navigable Small World)
   - O(log n) search complexity
   - Fast with small dataset (20 cases)

### Timing Breakdown

```
Search Process Timeline:

T+0ms     Query received
T+10ms    Input validation
T+20ms    Embedding generated (Query → vector)
T+50ms    Similarity search in ChromaDB
T+75ms    Response formatted
T+100ms   HTML generated
T+150ms   Response sent to browser

Total: ~150ms (backend processing)
```

---

## 🧪 Testing Endpoints

### Using curl

```bash
# Health check
curl http://localhost:5000/api/health

# Get statistics
curl http://localhost:5000/api/cases/stats

# List all cases
curl http://localhost:5000/api/cases/list

# Search (POST with JSON)
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "chest pain",
    "num_results": 5
  }'
```

---

## 🔧 Configuration

### Adjustable Parameters

**In rag_pipeline.py:**
```python
# Vector model choice
embedding_model = "all-MiniLM-L6-v2"  # Change for different model

# Database location
persist_directory = "./chroma_data"    # Change storage location

# Search parameters
n_results = 5                          # Default results to return
max_results = 10                       # Maximum allowed
```

**In app.py:**
```python
# Server configuration
host = '0.0.0.0'      # Accessible from all interfaces
port = 5000           # Flask default port
debug = True          # Enable debug mode
```

---

## 📊 System Metrics

### Resource Usage

| Resource | Value | Notes |
|----------|-------|-------|
| Memory | ~200-300 MB | Python + models |
| CPU | Low usage | Most time in I/O |
| Disk | ~50 MB | Vector DB + models |
| Network | Minimal | Only AJAX calls |

### Scalability

| Metric | Current | With 1000 cases |
|--------|---------|-----------------|
| Index size | ~2 MB | ~100 MB |
| Search time | <50ms | <100ms |
| Memory | 300 MB | 500 MB |

---

## 🚀 Deployment Considerations

### Development → Production

```
Development:
- Flask debug=True
- Localhost only
- No SSL

Production:
- Use WSGI server (Gunicorn)
- Run behind reverse proxy (Nginx)
- Enable SSL/TLS
- Add authentication
- Set debug=False
```

### Example Production Setup

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Behind Nginx reverse proxy
# Nginx listens on 80/443
# Proxies to Gunicorn on 5000
```

---

## 📝 Code Comments Reference

Each module includes comprehensive comments:

**app.py**:
- Line-by-line explanation of routes
- Request/response format documentation
- Error handling explanation

**rag_pipeline.py**:
- RAG pipeline workflow documented
- Similarity search algorithm explained
- Response generation logic documented

**embeddings.py**:
- Embedding generation process
- Why Sentence Transformers chosen
- Batch processing benefits

**index.html**:
- HTML structure commentary
- Bootstrap grid explanation
- Form validation notes

**script.js**:
- Event listener documentation
- API communication flow
- Error handling strategy

---

## 🎓 Learning Outcomes

After studying this codebase, you'll understand:

1. ✅ **RAG Architecture**: How retrieval + generation works
2. ✅ **Vector Embeddings**: Text → numerical representation
3. ✅ **Similarity Search**: Finding related items in vectors
4. ✅ **Flask Backend**: REST API development
5. ✅ **Frontend-Backend Integration**: AJAX communication
6. ✅ **Data Processing**: Loading and indexing data
7. ✅ **UI/UX**: Clean interface design
8. ✅ **Error Handling**: Graceful failure management

---

**This architecture ensures a robust, scalable, and maintainable system for clinical case retrieval and learning!**
