"""CaseMatrix AI Flask application."""

from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from rag_pipeline import get_rag_pipeline


app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

rag_pipeline = get_rag_pipeline()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


@app.route("/query", methods=["POST"])
def query_cases():
    try:
        payload = request.get_json(silent=True) or {}
        query = str(payload.get("query", "")).strip()

        if not query:
            return jsonify({"error": "query is required"}), 400

        try:
            num_results = int(payload.get("num_results", 3))
        except (TypeError, ValueError):
            num_results = 3

        # Keep retrieval range predictable for this dataset-driven API.
        if num_results < 3:
            num_results = 3
        if num_results > 5:
            num_results = 5

        result = rag_pipeline.process_query(query, n_results=num_results)
        # Provide both key styles so either frontend variant works:
        # - older frontend expects `response` and `retrieved_cases` (backend/app.py)
        # - this app uses `answer` and `cases` (root rag_pipeline)
        return jsonify(
            {
                "success": True,
                "query": query,
                "answer": result.get("answer"),
                "cases": result.get("cases"),
                "response": result.get("answer"),
                "retrieved_cases": result.get("cases"),
                "num_results": result.get("num_results"),
                "timestamp": datetime.now().isoformat(),
            }
        ), 200
    except Exception as exc:
        return jsonify({"error": "Internal server error", "message": str(exc)}), 500


@app.route("/api/search", methods=["POST"])
def legacy_query_cases():
    return query_cases()


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
