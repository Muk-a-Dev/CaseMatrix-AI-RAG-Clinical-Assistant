/*
   CaseMatrix AI — frontend interactions
*/

const searchForm = document.getElementById("searchForm");
const queryCard = document.querySelector(".query-card");
const queryInput = document.getElementById("queryInput");
const numResultsSlider = document.getElementById("numResults");
const resultCountDisplay = document.getElementById("resultCount");
const searchBtn = document.getElementById("searchBtn");
const searchBtnLabel = searchBtn ? searchBtn.querySelector(".submit-btn__label") : null;
const DEFAULT_SEARCH_LABEL = "Search similar cases";
const loadingSpinner = document.getElementById("loadingSpinner");
const errorAlert = document.getElementById("errorAlert");
const errorMessage = document.getElementById("errorMessage");
const errorClose = document.getElementById("errorClose");
const resultsSection = document.getElementById("resultsSection");
const responseContent = document.getElementById("responseContent");
const casesContainer = document.getElementById("casesContainer");
const caseCountDisplay = document.getElementById("caseCount");

function escapeHtml(text) {
    if (text == null) return "";
    const s = String(text);
    const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return s.replace(/[&<>"']/g, (ch) => map[ch] || ch);
}

numResultsSlider.addEventListener("input", function () {
    resultCountDisplay.textContent = this.value;
});

if (errorClose) {
    errorClose.addEventListener("click", hideError);
}

searchForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    await performSearch();
});

async function performSearch() {
    try {
        const query = queryInput.value.trim();
        const numResults = parseInt(numResultsSlider.value, 10);

        if (!query) {
            showError("Please enter a clinical query");
            return;
        }

        if (!searchBtn || !loadingSpinner) return;

        hideError();
        resultsSection.style.display = "none";
        loadingSpinner.style.display = "block";
        if (queryCard) queryCard.classList.add("is-querying");
        searchBtn.classList.add("is-loading");
        searchBtn.setAttribute("aria-busy", "true");
        if (searchBtnLabel) searchBtnLabel.textContent = "Searching…";
        searchBtn.disabled = true;

        const requestData = { query, num_results: numResults };

        const response = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData),
        });

        if (!response.ok) {
            let msg = "Search failed";
            try {
                const errData = await response.json();
                msg = errData.message || errData.error || msg;
            } catch {
                /* ignore */
            }
            throw new Error(msg);
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error("[CLIENT] Search error:", error);
        showError(error.message || "An error occurred during search");
    } finally {
        if (loadingSpinner) loadingSpinner.style.display = "none";
        if (queryCard) queryCard.classList.remove("is-querying");
        if (searchBtn) {
            searchBtn.classList.remove("is-loading");
            searchBtn.removeAttribute("aria-busy");
            if (searchBtnLabel) searchBtnLabel.textContent = DEFAULT_SEARCH_LABEL;
            searchBtn.disabled = false;
        }
    }
}

function displayResults(data) {
    const answerText = data.answer != null ? data.answer : data.response;
    responseContent.textContent = answerText != null ? String(answerText) : "";

    const cases = data.retrieved_cases || data.cases || [];
    caseCountDisplay.textContent = String(cases.length);

    casesContainer.innerHTML = "";
    if (cases.length > 0) {
        cases.forEach((caseData, index) => {
            casesContainer.appendChild(createCaseElement(caseData, index + 1));
        });
    } else {
        casesContainer.innerHTML = '<p class="field-hint" style="text-align:center;">No cases retrieved.</p>';
    }

    resultsSection.style.display = "block";
    const anchor = document.getElementById("results-anchor");
    setTimeout(() => {
        (anchor || resultsSection).scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
}

function formatSymptomListHtml(metadata) {
    const list = metadata.symptoms_list;
    if (Array.isArray(list) && list.length > 0) {
        const items = list
            .map((s) => String(s).trim())
            .filter(Boolean)
            .map((s) => `<li>${escapeHtml(s.replace(/_/g, " "))}</li>`)
            .join("");
        return `<ul class="case-symptom-list">${items}</ul>`;
    }
    const fallback = metadata.symptoms || "Not specified";
    return `<div class="case-section-content">${escapeHtml(fallback)}</div>`;
}

function createCaseElement(caseData, index) {
    const caseDiv = document.createElement("div");
    caseDiv.className = "case-card slide-in";

    const metadata = caseData.metadata || {};
    const rawScore = Number(caseData.similarity_score);
    const similarityDecimal = Number.isFinite(rawScore) ? rawScore.toFixed(3) : "—";
    const similarityPercent = Number.isFinite(rawScore)
        ? (rawScore <= 1 ? (rawScore * 100).toFixed(1) : rawScore.toFixed(1))
        : "—";

    const title = metadata.title || metadata.diagnosis || "Clinical case";
    const diagnosis = metadata.diagnosis || title;
    const treatment = metadata.treatment || "Not specified";
    const age = metadata.patient_age ? `${escapeHtml(metadata.patient_age)} years old` : "Not in dataset";
    const gender = metadata.gender ? escapeHtml(metadata.gender) : "Not in dataset";
    const duration = metadata.duration_days ? escapeHtml(String(metadata.duration_days).trim()) : "—";

    const symptomsBlock = formatSymptomListHtml(metadata);

    caseDiv.innerHTML = `
        <div class="case-card__top">
            <span class="case-id">Match #${index}</span>
            <span class="similarity-badge" title="Cosine similarity (TF‑IDF), 0–1">${escapeHtml(String(similarityPercent))}% · ${escapeHtml(String(similarityDecimal))}</span>
        </div>
        <div class="case-title">
            ${escapeHtml(title)}
            <span class="case-title__sub">Dataset row ID: ${escapeHtml(String(caseData.case_id || "—"))}</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">Condition / disease (CSV)</div>
            <div class="case-section-content">${escapeHtml(diagnosis)}</div>
        </div>
        <div class="case-section">
            <div class="case-section-title">Symptoms from record</div>
            ${symptomsBlock}
        </div>
        <div class="case-section">
            <div class="case-section-title">Educational note</div>
            <div class="case-section-content">${escapeHtml(treatment)}</div>
        </div>
        <div class="case-meta">
            <span>Demographics in CSV: age ${age}, gender ${gender}</span>
            <span class="case-meta__sep">·</span>
            <span>Duration field: ${duration}</span>
        </div>
    `;

    return caseDiv;
}

function showError(message) {
    errorMessage.textContent = message;
    errorAlert.style.display = "block";
    setTimeout(() => hideError(), 8000);
}

function hideError() {
    errorAlert.style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    if (queryInput) queryInput.focus();
});
