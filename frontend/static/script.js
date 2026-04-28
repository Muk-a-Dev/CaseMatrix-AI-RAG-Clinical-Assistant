/**
 * CASEMATRIX AI - FRONTEND JAVASCRIPT
 * ====================================
 * 
 * This script handles:
 * - Form submission and validation
 * - API communication with backend
 * - Results display and rendering
 * - Error handling
 * - UI interactions
 */

// ==================== DOM ELEMENTS ====================

const searchForm = document.getElementById('search-form');
const queryInput = document.getElementById('query-input');
const numResultsSlider = document.getElementById('num-results-slider');
const numResultsDisplay = document.getElementById('num-results-display');
const searchBtn = document.getElementById('search-btn');
const loadingSpinner = document.getElementById('loading-spinner');
const resultsSection = document.getElementById('results-section');
const noResultsSection = document.getElementById('no-results-section');
const responseContent = document.getElementById('response-content');
const casesContainer = document.getElementById('cases-container');
const errorAlert = document.getElementById('error-alert');
const errorMessage = document.getElementById('error-message');

// ==================== EVENT LISTENERS ====================

/**
 * Update the number of results display when slider changes
 */
numResultsSlider.addEventListener('input', function () {
    numResultsDisplay.textContent = this.value;
});

/**
 * Handle form submission
 */
searchForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    
    // Get form values
    const query = queryInput.value.trim();
    const numResults = parseInt(numResultsSlider.value);
    
    // Validate
    if (!query) {
        showError('Please enter a clinical query');
        return;
    }
    
    if (query.length > 1000) {
        showError('Query must be less than 1000 characters');
        return;
    }
    
    // Perform search
    await performSearch(query, numResults);
});

// ==================== SEARCH FUNCTION ====================

/**
 * Perform the clinical case search
 * @param {string} query - The clinical query
 * @param {number} numResults - Number of results to retrieve
 */
async function performSearch(query, numResults) {
    console.log('[SEARCH] Starting search...');
    console.log('[SEARCH] Query:', query);
    console.log('[SEARCH] Num Results:', numResults);
    
    // Hide previous results
    resultsSection.style.display = 'none';
    noResultsSection.style.display = 'none';
    hideError();
    
    // Show loading spinner
    loadingSpinner.style.display = 'block';
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
    
    try {
        // Call backend API
        const response = await fetch('http://127.0.0.1:5001/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                num_results: numResults
            })
        });
        
        console.log('[RESPONSE] Status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('[DATA] Received response:', data);
        
        if (!data.success && !data.answer && !data.cases) {
            throw new Error(data.message || 'Search failed');
        }
        
        // Display results
        displayResults(data);
        
        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
    } catch (error) {
        console.error('[ERROR] Search failed:', error);
        showError(`Search failed: ${error.message}`);
    } finally {
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<span class="button-icon">🚀</span> Search Cases';
    }
}

// ==================== DISPLAY RESULTS ====================

/**
 * Display search results
 * @param {object} data - Response data from backend
 */
function displayResults(data) {
    console.log('[DISPLAY] Displaying results...');
    
    // Display AI-generated response
    responseContent.innerHTML = data.answer || data.response || '<p>No answer returned.</p>';
    
    // Display retrieved cases
    casesContainer.innerHTML = '';
    
    const cases = data.cases || data.retrieved_cases || [];

    if (cases.length === 0) {
        noResultsSection.style.display = 'block';
        console.log('[DISPLAY] No results to display');
        return;
    }
    
    // Create case cards
    cases.forEach((caseData, index) => {
        const caseElement = createCaseElement(caseData, index + 1);
        casesContainer.appendChild(caseElement);
    });
    
    // Show results section
    resultsSection.style.display = 'block';
    console.log('[DISPLAY] Results displayed successfully');
}

/**
 * Create a case card element
 * @param {object} caseData - Case data from API
 * @param {number} index - Case number (1-based)
 * @returns {HTMLElement} Case card element
 */
function createCaseElement(caseData, index) {
    // Extract data
    const caseId = caseData.case_id || 'Unknown';
    const metadata = caseData.metadata || {};
    const title = metadata.title || 'Case Title';
    const symptoms = metadata.symptoms || 'Not specified';
    const diagnosis = metadata.diagnosis || 'Not specified';
    const treatment = metadata.treatment || 'Not specified';
    const patientAge = metadata.patient_age || 'Not specified';
    const gender = metadata.gender || 'Not specified';
    const durationDays = metadata.duration_days || 'Not specified';
    const similarityScore = caseData.similarity_score || 0;
    
    // Create card element
    const card = document.createElement('div');
    card.className = 'col-lg-6 case-card';
    
    // Build HTML
    const html = `
        <div class="card h-100">
            <!-- Card Header -->
            <div class="case-card-header">
                <span class="case-id-badge">${caseId}</span>
                <h5 class="case-title">${escapeHtml(title)}</h5>
            </div>
            
            <!-- Card Body -->
            <div class="case-card-body">
                <!-- Similarity Score -->
                <div class="mb-3">
                    <span class="similarity-score">
                        Similarity: ${(similarityScore * 100).toFixed(1)}%
                    </span>
                </div>
                
                <!-- Case Details -->
                <div class="case-info-section">
                    <div class="case-info-label">👤 Patient Info</div>
                    <div class="case-info-content">
                        <p class="mb-1">Age: ${escapeHtml(patientAge)} | Gender: ${escapeHtml(gender)}</p>
                        <p class="mb-0">Duration: ${escapeHtml(durationDays)} days</p>
                    </div>
                </div>
                
                <div class="case-info-section">
                    <div class="case-info-label">🔍 Symptoms</div>
                    <div class="case-info-content">
                        <p class="mb-0">${escapeHtml(symptoms)}</p>
                    </div>
                </div>
                
                <div class="case-info-section">
                    <div class="case-info-label">🏥 Diagnosis</div>
                    <div class="case-info-content">
                        <p class="mb-0">${escapeHtml(diagnosis)}</p>
                    </div>
                </div>
                
                <div class="case-info-section">
                    <div class="case-info-label">💊 Treatment</div>
                    <div class="case-info-content">
                        <p class="mb-0">${escapeHtml(treatment)}</p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="case-footer">
                    Case #${index} | Retrieved from Clinical Database
                </div>
            </div>
        </div>
    `;
    
    card.innerHTML = html;
    return card;
}

// ==================== ERROR HANDLING ====================

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    console.error('[ERROR]', message);
    errorMessage.textContent = message;
    errorAlert.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
    errorAlert.style.display = 'none';
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== PAGE INITIALIZATION ====================

/**
 * Initialize the page
 */
function initializePage() {
    console.log('[INIT] Initializing CaseMatrix AI...');
    
    // Focus on query input
    queryInput.focus();
    
    // Set initial slider value display
    numResultsDisplay.textContent = numResultsSlider.value;
    
    console.log('[INIT] Page initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializePage);

console.log('[APP] CaseMatrix AI Frontend Loaded');
console.log('[APP] Backend API: http://127.0.0.1:5001/query');
