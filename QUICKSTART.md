# CaseMatrix AI - Quick Start Guide

## ⚡ 5-Minute Quick Start

### 1. Open Terminal & Navigate to Project
```bash
cd /Users/macmuk/Desktop/CaseMatrix-AI-RAG-Clinical-Assistant
```

### 2. Create Virtual Environment (First Time Only)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

### 4. Run the Server
```bash
python app.py
```

### 5. Open Browser
```
http://localhost:5000
```

### 6. Start Searching!
- Enter a clinical query: "Patient with chest pain"
- Click "Search Similar Cases"
- Review retrieved cases and AI response

---

## 📋 What Happens on Startup

```
✓ Flask server initializes
✓ RAG Pipeline loads
✓ Clinical cases load from JSON
✓ Vector embeddings generated (if first time)
✓ ChromaDB index created
✓ Server ready on port 5000
```

First run may take 1-2 minutes. Subsequent runs are faster.

---

## 🔍 Test Queries to Try

```
1. "Type 2 Diabetes with hypertension symptoms"

2. "Sudden chest pain radiating to left arm with shortness of breath"

3. "High fever productive cough and chest pain"

4. "Facial drooping and arm weakness sudden onset"

5. "Severe headache chest pain altered mental status"
```

---

## 📊 Project Structure Quick Reference

```
app.py                 ← Start here! Main Flask app
├── templates/
│   └── index.html     ← Web interface
├── static/
│   ├── style.css      ← Styling
│   └── script.js      ← Frontend logic
├── rag_pipeline.py    ← Search engine
├── embeddings.py      ← Vector conversion
├── data/
│   └── clinical_cases.json  ← 20 clinical cases
└── requirements.txt   ← Dependencies
```

---

## 🛑 Stop Server

Press `Ctrl+C` in terminal

---

## ❓ Common Commands

| Command | Purpose |
|---------|---------|
| `python app.py` | Start server |
| `pip install -r requirements.txt` | Install dependencies |
| `source venv/bin/activate` | Activate virtual env |
| `deactivate` | Deactivate virtual env |
| `curl http://localhost:5000/api/health` | Check server status |

---

## 📞 Troubleshooting

**Server won't start?**
- Check if port 5000 is free
- Ensure virtual environment is activated

**No results?**
- Check your query isn't empty
- Ensure you have internet (for embedding model)

**Module errors?**
- Reinstall: `pip install -r requirements.txt`

---

## 🎓 Architecture Overview

```
User Query
    ↓
[API: /api/search]
    ↓
[embeddings.py] - Convert query to vector
    ↓
[rag_pipeline.py] - Search ChromaDB
    ↓
[Retrieved Cases] - Get top 5 similar
    ↓
[Generate Response] - Create summary
    ↓
[HTML Response] - Display in browser
```

---

**That's it! You're ready to go! 🚀**
