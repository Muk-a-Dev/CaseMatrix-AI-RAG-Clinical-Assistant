# CaseMatrix AI - Clinical Case Intelligence Tool

Simple Flask + TF-IDF project for clinical case retrieval.

The backend automatically loads [data/dataset.csv](data/dataset.csv) (Kaggle symptom dataset) using pandas.

## Run

```bash
pip3 install -r requirements.txt
python3 app.py
```

## Open the app

Open `frontend/templates/index.html` in your browser, or visit `http://127.0.0.1:5001` after starting the Flask server.

## API

`POST http://127.0.0.1:5001/query`

Example body:

```json
{
  "query": "Patient with chest pain and shortness of breath",
  "num_results": 3
}
```

## Project files

- `app.py` - Flask backend
- `rag_pipeline.py` - TF-IDF retrieval logic
- `requirements.txt` - Minimal dependencies
- `data/clinical_cases.json` - Sample clinical cases
- `frontend/templates/index.html` - Frontend UI
- `frontend/static/script.js` - Frontend API call
- `frontend/static/style.css` - Frontend styling

## Notes

- The backend uses `flask`, `flask-cors`, `numpy`, and `scikit-learn` only.
- The backend uses `pandas` to read [data/dataset.csv](data/dataset.csv).
- The backend returns `answer` and `cases` from `POST /query`.
- The frontend posts to `http://127.0.0.1:5001/query`.