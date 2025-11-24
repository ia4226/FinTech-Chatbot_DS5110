/* ====================================
   STATE MANAGEMENT
   ==================================== */
const state = {
    currentCompany: null,
    currentReport: null,
    isLoading: false,
    messages: [],
};

// Track active Chart.js instance so we can refresh on theme changes
let activeChart = null;

// Lightweight DOM mapping and small helpers (restore originals if missing)
const dom = {
    messagesArea: document.getElementById('messages-area'),
    queryInput: document.getElementById('query-input'),
    sendButton: document.getElementById('send-button'),
    reportModal: document.getElementById('report-modal'),
    reportContent: document.getElementById('report-content'),
    reportModalTitle: document.getElementById('report-modal-title'),
    modalDownloadBtn: document.getElementById('modal-download-btn'),
    toastContainer: document.getElementById('toast-container'),
    loadingIndicator: document.getElementById('loading-indicator')
};

function showEmptyState() {
    // If empty state exists, ensure it's visible when there are no messages
    const empty = document.querySelector('.empty-state');
    if (!empty) return;
    // show if messages area is empty
    if (!dom.messagesArea || dom.messagesArea.children.length === 0) empty.style.display = '';
    else empty.style.display = 'none';
}

function addMessage(text, isUser = false) {
    if (!dom.messagesArea) return;
    const messageGroup = document.createElement('div');
    messageGroup.className = isUser ? 'message-group user' : 'message-group assistant';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerText = text;

    messageGroup.appendChild(bubble);
    dom.messagesArea.appendChild(messageGroup);
    setTimeout(() => { dom.messagesArea.scrollTop = dom.messagesArea.scrollHeight; }, 0);
    showEmptyState();
}

function setLoading(loading) {
    state.isLoading = loading;
    if (!dom.loadingIndicator) return;
    dom.loadingIndicator.style.display = loading ? '' : 'none';
}

async function post(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return res.json();
}

function addAnalysisCard(title, data, type) {
    const card = document.createElement('div');
    card.className = 'analysis-card';

    if (type === 'stock') {
        let html = `
                <h3>
                    <svg class="analysis-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                    </svg>
                    ${title}
                </h3>
                <div class="stock-info-grid">
            `;

        if (data && typeof data === 'object') {
            Object.entries(data).forEach(([key, value]) => {
                if (value !== 'N/A' && value !== null) {
                    const formattedKey = key.replace(/([A-Z])/g, ' $1').trim();
                    html += `
                            <div class="stock-metric">
                                <div class="metric-label">${formattedKey}</div>
                                <div class="metric-value">${formatValue(value)}</div>
                            </div>
                        `;
                }
            });
        }

        html += '</div>';
        card.innerHTML = html;
    } else if (type === 'news') {
        let html = `
                <h3>
                    <svg class="analysis-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                    </svg>
                    ${title}
                </h3>
                <ul class="news-list">
            `;

        if (Array.isArray(data)) {
            data.forEach((item, idx) => {
                html += `<li class="news-item">${item}</li>`;
            });
        }

        html += '</ul>';
        card.innerHTML = html;
    }

    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group assistant';
    messageGroup.appendChild(card);
    dom.messagesArea.appendChild(messageGroup);

    setTimeout(() => {
        dom.messagesArea.scrollTop = dom.messagesArea.scrollHeight;
    }, 0);
}

function renderPriceChart(chartData, company) {
    const chartCanvas = document.getElementById('priceChart');
    if (!chartCanvas) return;

    // If a chart already exists, destroy it before creating a new one
    try {
        if (activeChart && typeof activeChart.destroy === 'function') {
            activeChart.destroy();
            activeChart = null;
        }
    } catch (e) {
        console.warn('Failed to destroy previous chart', e);
    }

    const ctx = chartCanvas.getContext('2d');
    const dates = chartData.map(d => d.date);
    const prices = chartData.map(d => d.close);

    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const currentPrice = prices[prices.length - 1];
    const startPrice = prices[0];
    const priceChange = ((currentPrice - startPrice) / startPrice * 100).toFixed(2);
    const isPositive = priceChange >= 0;

    // derive colors from CSS variables to match theme
    const css = getComputedStyle(document.documentElement);
    const success = css.getPropertyValue('--success-600').trim() || '#22c55e';
    const error = css.getPropertyValue('--error-600').trim() || '#ef4444';
    const gridColor = css.getPropertyValue('--gray-200').trim() || 'rgba(229,231,235,0.5)';
    const tickColor = css.getPropertyValue('--gray-500').trim() || '#9ca3af';

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Stock Price',
                data: prices,
                borderColor: isPositive ? success : error,
                backgroundColor: isPositive ? hexToRgba(success, 0.09) : hexToRgba(error, 0.09),
                borderWidth: 2,
                fill: true,
                tension: 0.36,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointBackgroundColor: isPositive ? success : error,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    borderColor: isPositive ? success : error,
                    borderWidth: 1,
                    displayColors: false,
                    callbacks: { label: function (context) { return '$' + context.parsed.y.toFixed(2); } }
                }
            },
            scales: {
                x: { display: true, grid: { display: false }, ticks: { maxTicksLimit: 6, font: { size: 12 }, color: tickColor } },
                y: { display: true, beginAtZero: false, grid: { color: gridColor, drawBorder: false }, ticks: { font: { size: 12 }, color: tickColor, callback: function (v) { return '$' + v.toFixed(0); } } }
            }
        }
    });

    // Store reference so we can update/destroy later
    try {
        // Chart.js returns the chart instance from the constructor
        activeChart = Chart.getChart(ctx) || null;
    } catch (e) {
        // Fallback: Chart constructor may have returned instance directly in some builds
        activeChart = null;
    }
}

// Helper: convert hex to rgba
function hexToRgba(hex, alpha = 1) {
    try {
        const h = hex.replace('#', '').trim();
        const bigint = parseInt(h.length === 3 ? h.split('').map(c => c + c).join('') : h, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    } catch (e) {
        return `rgba(99,102,241,${alpha})`;
    }
}


function formatValue(value) {
    if (typeof value === 'number') {
        if (value > 1000000) return '$' + (value / 1000000).toFixed(1) + 'M';
        if (value > 1000) return '$' + (value / 1000).toFixed(1) + 'K';
        return '$' + value.toFixed(2);
    }
    return String(value);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
    <span class="toast-message">${message}</span>
  `;

    dom.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

/* ====================================
   MODAL FUNCTIONS
   ==================================== */
function formatReportHTML(plainText) {
    // Escape HTML special characters
    let html = plainText
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    // Convert markdown-style headers
    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    html = html.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');

    // Convert bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

    // Convert italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');

    // Convert tables (markdown style)
    html = html.replace(/\n\| (.*?) \|\n\| (.*?) \|\n/gm, function (match, header, divider) {
        const headers = header.split('|').map(h => h.trim()).filter(h => h);
        const cols = divider.split('|').filter(h => h.trim());
        if (cols.length === headers.length) {
            const headerHtml = '<thead><tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr></thead>';
            return '\n<table>' + headerHtml + '<tbody>\n';
        }
        return match;
    });

    html = html.replace(/\| (.*?) \|/gm, function (match) {
        const cells = match.split('|').map(c => c.trim()).filter(c => c && c !== '---');
        if (cells.length > 0 && !match.includes('---')) {
            return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
        }
        return match;
    });

    // Convert line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');

    return html;
}

function openReportModal(company, report, stockInfo, chartData) {
    dom.reportModalTitle.textContent = `${company} Financial Report`;

    // Create professional structured report with HTML layout
    const reportHTML = `
        <div class="dashboard-report">
            <!-- Header Section -->
            <div class="report-header-section">
                <div class="company-title">${company}</div>
                <div class="report-timestamp">Generated ${new Date().toLocaleDateString()} • Financial Analysis</div>
            </div>

            <!-- Stock Information Widget -->
            <div class="metrics-section">
                <h3 class="section-title">Stock Information</h3>
                <div class="stock-widget">
                    ${stockInfo && Object.entries(stockInfo).map(([key, value]) => {
        if (value === 'N/A' || value === null) return '';
        const label = key.replace(/([A-Z])/g, ' $1').trim();
        return `
                            <div class="stock-metric-row">
                                <span class="metric-row-label">${label}</span>
                                <span class="metric-row-value">${formatStockValue(value)}</span>
                            </div>
                        `;
    }).join('')}
                </div>
            </div>

            <!-- Price Chart -->
            ${chartData && chartData.length > 0 ? `
            <div class="chart-section">
                <h3 class="section-title">12-Month Price Performance</h3>
                <canvas id="priceChart" class="price-chart" height="80"></canvas>
            </div>
            ` : ''}

            <!-- Report Content -->
            <div class="report-content-section">
                <h3 class="section-title">Detailed Analysis</h3>
                <div class="report-formatter">
                    ${formatReportHTML(report)}
                </div>
            </div>
        </div>
    `;

    dom.reportContent.innerHTML = reportHTML;

    // Initialize chart if data exists
    if (chartData && chartData.length > 0) {
        setTimeout(() => {
            renderPriceChart(chartData, company);
        }, 100);
    }

    dom.reportModal.classList.add('active');
    state.currentReport = { company, report, stockInfo, chartData };
}

// Theme helpers were removed to restore original single-theme behavior.
function formatStockValue(value) {
    if (typeof value === 'number') {
        if (value > 1000000000) return '$' + (value / 1000000000).toFixed(2) + 'B';
        if (value > 1000000) return '$' + (value / 1000000).toFixed(2) + 'M';
        if (value > 1000) return '$' + (value / 1000).toFixed(2) + 'K';
        return '$' + value.toFixed(2);
    }
    return String(value);
}

function closeReportModal() {
    dom.reportModal.classList.remove('active');
}

function downloadReport() {
    if (!state.currentReport) return;

    const { company, report } = state.currentReport;
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${company.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('Report downloaded successfully', 'success');
}

/* ====================================
   MAIN FLOW: GENERATE REPORT
   ==================================== */
async function generateReport(query) {
    if (!query.trim()) {
        showToast('Please enter a company name or query', 'warning');
        return;
    }

    try {
        setLoading(true);

        // Hide empty state when first query runs
        const empty = document.querySelector('.empty-state');
        if (empty) empty.style.display = 'none';

        // Add user message
        addMessage(query, true);

        // Add thinking message
        addMessage('Analyzing your query...', false);

        // Call API
        const data = await post('/api/report', { query });

        // Remove thinking message
        dom.messagesArea.removeChild(dom.messagesArea.lastChild);

        // Update state
        state.currentCompany = data.company;

        // Add company identification
        addMessage(`Analyzing ${data.company}...`, false);

        // Add stock info card
        if (data.stock_info) {
            addAnalysisCard('Stock Information', data.stock_info, 'stock');
        }

        // Add news summaries
        if (data.news_summaries && data.news_summaries.length > 0) {
            addAnalysisCard('Recent News', data.news_summaries, 'news');
        }

        // Add detailed report
        if (data.detailed_report) {
            const reportBtn = document.createElement('button');
            reportBtn.className = 'btn btn-primary';
            reportBtn.textContent = 'View Full Report';
            reportBtn.addEventListener('click', () => {
                openReportModal(data.company, data.detailed_report, data.stock_info, data.chart_data);
            });

            // Format the report text for consistent display
            const formattedReport = formatReportHTML(data.detailed_report);

            const messageGroup = document.createElement('div');
            messageGroup.className = 'message-group assistant';
            const bubble = document.createElement('div');
            bubble.className = 'analysis-card analysis-report';
            bubble.innerHTML = `
        <h3>
          <svg class="analysis-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="13" x2="18" y2="13"></line>
            <line x1="12" y1="17" x2="18" y2="17"></line>
          </svg>
          AI Analysis
        </h3>
        <div class="report-preview report-formatter">
          ${formattedReport}
        </div>
      `;
            bubble.appendChild(reportBtn);
            messageGroup.appendChild(bubble);
            dom.messagesArea.appendChild(messageGroup);

            dom.messagesArea.scrollTop = dom.messagesArea.scrollHeight;
        }

        showToast('Analysis complete', 'success');
    } catch (error) {
        console.error('Error:', error);
        addMessage(`Error: ${error.message}`, false);
        showToast('Failed to generate report. Please try again.', 'error');
    } finally {
        setLoading(false);
    }
}

/* ====================================
   EVENT LISTENERS
   ==================================== */
if (dom.queryInput) {
    dom.queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !state.isLoading) {
            generateReport(dom.queryInput.value);
            dom.queryInput.value = '';
        }
    });
}

if (dom.sendButton) {
    dom.sendButton.addEventListener('click', () => {
        if (!state.isLoading) {
            generateReport(dom.queryInput ? dom.queryInput.value : '');
            if (dom.queryInput) dom.queryInput.value = '';
        }
    });
}

if (dom.modalDownloadBtn) dom.modalDownloadBtn.addEventListener('click', downloadReport);

const modalClose = document.querySelector('.modal-close');
const modalCloseBtn = document.querySelector('.modal-close-btn');
if (modalClose) modalClose.addEventListener('click', closeReportModal);
if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeReportModal);

// Close modal on outside click
if (dom.reportModal) {
    dom.reportModal.addEventListener('click', (e) => {
        if (e.target === dom.reportModal) {
            closeReportModal();
        }
    });
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && dom.reportModal && dom.reportModal.classList.contains('active')) {
        closeReportModal();
    }
});

// Sidebar navigation
document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach((i) => i.classList.remove('active'));
        item.classList.add('active');
    });
});

/* ====================================
   INITIALIZATION
   ==================================== */
document.addEventListener('DOMContentLoaded', () => {
    // Make sure empty state is visible on page load
    const empty = document.querySelector('.empty-state');
    if (empty) empty.style.display = '';
    
    if (dom.queryInput) dom.queryInput.focus();

    // Wire suggestion chips to populate input and trigger analysis
    document.querySelectorAll('.suggestion-chip').forEach((chip) => {
        chip.addEventListener('click', (e) => {
            e.preventDefault();
            const q = chip.dataset.query || chip.textContent || '';
            if (dom.queryInput) dom.queryInput.value = q;
            // Trigger analysis
            if (!state.isLoading) generateReport(q);
        });
    });
});

