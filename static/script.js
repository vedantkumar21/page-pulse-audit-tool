/**
 * Page Pulse - Website Audit Tool Client Script
 * Handles asynchronous audit requests, UI state transitions, SVG score gauge animations,
 * dynamic metrics rendering, toast notifications, and copy report tools.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const auditForm = document.getElementById('auditForm');
    const urlInput = document.getElementById('urlInput');
    const clearBtn = document.getElementById('clearBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnSpinner = document.getElementById('btnSpinner');
    const sampleChips = document.querySelectorAll('.sample-chip');
    
    // UI Container Elements
    const loadingState = document.getElementById('loadingState');
    const loadingStatusText = document.getElementById('loadingStatusText');
    const resultsSection = document.getElementById('resultsSection');
    const toastContainer = document.getElementById('toastContainer');
    
    // Report Elements
    const reportUrlLink = document.getElementById('reportUrlLink');
    const copyReportBtn = document.getElementById('copyReportBtn');
    const scoreGaugeProgress = document.getElementById('scoreGaugeProgress');
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreBadge = document.getElementById('scoreBadge');
    const scoreSubtitle = document.getElementById('scoreSubtitle');
    const scoreBreakdownList = document.getElementById('scoreBreakdownList');
    
    // Metric Value Elements
    const valStatusCode = document.getElementById('valStatusCode');
    const valResponseTime = document.getElementById('valResponseTime');
    const valConnectionHealth = document.getElementById('valConnectionHealth');
    const valPageTitle = document.getElementById('valPageTitle');
    const valWordCount = document.getElementById('valWordCount');
    const valH1Count = document.getElementById('valH1Count');
    const valH1Status = document.getElementById('valH1Status');
    const valTotalImages = document.getElementById('valTotalImages');
    const valMissingAlt = document.getElementById('valMissingAlt');
    const valAltCoverage = document.getElementById('valAltCoverage');
    const valMetaDesc = document.getElementById('valMetaDesc');
    const valCanonical = document.getElementById('valCanonical');
    const valRobots = document.getElementById('valRobots');
    
    // Store latest report data for copy functionality
    let currentReport = null;

    /* ==========================================================================
       Input Handling & Clear Button Logic
       ========================================================================== */
    
    urlInput.addEventListener('input', () => {
        clearBtn.style.display = urlInput.value.trim() ? 'block' : 'none';
    });

    clearBtn.addEventListener('click', () => {
        urlInput.value = '';
        clearBtn.style.display = 'none';
        urlInput.focus();
    });

    // Sample Chips Click Handlers
    sampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const sampleUrl = chip.getAttribute('data-url');
            if (sampleUrl) {
                urlInput.value = sampleUrl;
                clearBtn.style.display = 'block';
                triggerAudit(sampleUrl);
            }
        });
    });

    /* ==========================================================================
       Form Submission & Async Audit Trigger
       ========================================================================== */

    auditForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const rawUrl = urlInput.value.trim();
        
        if (!rawUrl) {
            showToast('Input Required', 'Please enter a valid website URL to analyze.', 'error');
            urlInput.focus();
            return;
        }

        triggerAudit(rawUrl);
    });

    async function triggerAudit(rawUrl) {
        // UI Loading State Transition
        setLoading(true);
        resultsSection.style.display = 'none';
        loadingState.style.display = 'block';
        loadingStatusText.textContent = 'Connecting to server and analyzing DOM...';
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ url: rawUrl })
            });

            const data = await response.json();

            if (!response.ok || data.success === false) {
                const errorMsg = data.error || 'An unexpected error occurred while analyzing the page.';
                showToast('Audit Failed', errorMsg, 'error');
                loadingState.style.display = 'none';
                return;
            }

            // Store current report
            currentReport = data;

            // Update UI with audit results
            renderAuditReport(data);
            
            // Show Success Notification if score is good
            showToast('Audit Complete', `Successfully analyzed ${data.target_url}`, 'success');

        } catch (err) {
            console.error('Audit API fetch exception:', err);
            showToast('Network Error', 'Unable to reach backend API. Check your internet connection.', 'error');
            loadingState.style.display = 'none';
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        analyzeBtn.disabled = isLoading;
        btnSpinner.style.display = isLoading ? 'inline-block' : 'none';
        if (isLoading) {
            analyzeBtn.querySelector('.btn-text').style.opacity = '0.7';
        } else {
            analyzeBtn.querySelector('.btn-text').style.opacity = '1';
        }
    }

    /* ==========================================================================
       Report Data Rendering & Animations
       ========================================================================== */

    function renderAuditReport(report) {
        // Hide loader, reveal results
        loadingState.style.display = 'none';
        resultsSection.style.display = 'flex';
        
        // Scroll smoothly to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Header Url Link
        reportUrlLink.textContent = report.target_url;
        reportUrlLink.href = report.target_url;

        // 1. Render Gauge & SEO Score
        const score = report.seo_score || 0;
        animateScoreGauge(score);

        // 2. Render Score Breakdown List
        renderBreakdownList(report.score_breakdown);

        // 3. Render Metric Cards
        // Server & Status
        valStatusCode.textContent = report.status || '--';
        valStatusCode.className = 'metric-badge ' + getStatusBadgeClass(report.status);
        
        valResponseTime.textContent = report.response_time || '--';

        const timeNum = parseInt(report.response_time) || 0;
        if (timeNum < 400) {
            valConnectionHealth.textContent = '⚡ Excellent Response Speed';
            valConnectionHealth.className = 'status-indicator ok';
        } else if (timeNum < 1200) {
            valConnectionHealth.textContent = '⚡ Moderate Response Speed';
            valConnectionHealth.className = 'status-indicator warn';
        } else {
            valConnectionHealth.textContent = '🐢 Slow Response Time';
            valConnectionHealth.className = 'status-indicator error';
        }

        // Title & Content
        valPageTitle.textContent = report.title || 'Missing';
        valPageTitle.style.color = (report.title === 'Missing title tag') ? 'var(--color-danger)' : 'var(--text-primary)';
        
        valWordCount.textContent = (report.word_count !== undefined) ? report.word_count.toLocaleString() + ' words' : '--';

        // Headings
        valH1Count.textContent = report.h1_count !== undefined ? report.h1_count : '--';
        valH1Count.className = 'metric-badge ' + (report.h1_count > 0 ? 'status-200' : 'status-404');
        
        if (report.h1_count === 1) {
            valH1Status.textContent = '✓ Optimal (Exactly 1 H1 tag)';
            valH1Status.className = 'status-indicator ok';
        } else if (report.h1_count > 1) {
            valH1Status.textContent = '⚠ Multiple H1 tags found';
            valH1Status.className = 'status-indicator warn';
        } else {
            valH1Status.textContent = '✖ Missing H1 heading tag';
            valH1Status.className = 'status-indicator error';
        }

        // Media & Accessibility
        const totalImgs = report.total_images || 0;
        const missingAlt = report.images_without_alt || 0;
        valTotalImages.textContent = totalImgs;
        valMissingAlt.textContent = missingAlt;
        valMissingAlt.className = 'metric-badge ' + (missingAlt === 0 ? 'status-200' : 'status-404');

        if (totalImgs === 0) {
            valAltCoverage.textContent = '100% (No images)';
        } else {
            const coverage = Math.round(((totalImgs - missingAlt) / totalImgs) * 100);
            valAltCoverage.textContent = `${coverage}%`;
        }

        // Meta & Indexing
        valMetaDesc.textContent = report.meta_description || 'Missing';
        valMetaDesc.style.color = (report.meta_description === 'Missing meta description') ? 'var(--color-danger)' : 'var(--text-primary)';

        valCanonical.textContent = report.canonical || 'Not specified';
        valRobots.textContent = report.robots || 'Not specified';
    }

    /* ==========================================================================
       SVG Score Gauge & Counter Animation
       ========================================================================== */

    function animateScoreGauge(targetScore) {
        // Circumference of r=52 circle is 2 * PI * 52 = ~326.72
        const circumference = 326.72;
        const offset = circumference - (targetScore / 100) * circumference;
        
        // Reset gauge
        scoreGaugeProgress.style.strokeDashoffset = circumference;
        
        // Score Badge setup
        if (targetScore >= 80) {
            scoreBadge.textContent = 'Excellent';
            scoreBadge.className = 'score-badge badge-excellent';
            scoreGaugeProgress.style.stroke = 'var(--color-success)';
            scoreSubtitle.textContent = 'Great technical setup! Your website satisfies primary SEO criteria.';
        } else if (targetScore >= 50) {
            scoreBadge.textContent = 'Good / Warning';
            scoreBadge.className = 'score-badge badge-good';
            scoreGaugeProgress.style.stroke = 'var(--color-warning)';
            scoreSubtitle.textContent = 'Decent foundation, but several optimization areas require attention.';
        } else {
            scoreBadge.textContent = 'Needs Work';
            scoreBadge.className = 'score-badge badge-poor';
            scoreGaugeProgress.style.stroke = 'var(--color-danger)';
            scoreSubtitle.textContent = 'Critical technical SEO issues detected. Review breakdown below.';
        }

        // Animate stroke dashoffset
        setTimeout(() => {
            scoreGaugeProgress.style.strokeDashoffset = offset;
        }, 50);

        // Counter Animation
        let currentCount = 0;
        const duration = 1000;
        const increment = targetScore / (duration / 16);
        
        const counterInterval = setInterval(() => {
            currentCount += increment;
            if (currentCount >= targetScore) {
                scoreNumber.textContent = targetScore;
                clearInterval(counterInterval);
            } else {
                scoreNumber.textContent = Math.floor(currentCount);
            }
        }, 16);
    }

    function renderBreakdownList(breakdown) {
        scoreBreakdownList.innerHTML = '';
        if (!breakdown) return;

        Object.keys(breakdown).forEach(key => {
            const item = breakdown[key];
            const div = document.createElement('div');
            div.className = 'breakdown-item';
            
            const iconClass = item.pass ? 'fa-solid fa-circle-check pass' : 'fa-solid fa-circle-xmark fail';
            
            div.innerHTML = `
                <i class="${iconClass} breakdown-icon"></i>
                <span class="breakdown-text"><strong>+${item.points} pts:</strong> ${item.message}</span>
            `;
            scoreBreakdownList.appendChild(div);
        });
    }

    function getStatusBadgeClass(status) {
        if (!status) return 'status-error';
        if (status >= 200 && status < 300) return 'status-200';
        if (status >= 300 && status < 400) return 'status-warn';
        return 'status-404';
    }

    /* ==========================================================================
       Toast Manager
       ========================================================================== */

    function showToast(title, message, type = 'error') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const iconClass = type === 'success' ? 'fa-solid fa-circle-check' : 'fa-solid fa-triangle-exclamation';

        toast.innerHTML = `
            <i class="${iconClass} toast-icon"></i>
            <div class="toast-content">
                <div class="toast-title">${escapeHtml(title)}</div>
                <div class="toast-message">${escapeHtml(message)}</div>
            </div>
            <button class="toast-close" aria-label="Close alert">&times;</button>
        `;

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            removeToast(toast);
        });

        toastContainer.appendChild(toast);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            removeToast(toast);
        }, 5000);
    }

    function removeToast(toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    function escapeHtml(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    /* ==========================================================================
       Copy Report Tool
       ========================================================================== */

    copyReportBtn.addEventListener('click', () => {
        if (!currentReport) return;
        
        const text = `
=== PAGE PULSE WEBSITE AUDIT REPORT ===
Target URL: ${currentReport.target_url}
SEO Score: ${currentReport.seo_score}/100
HTTP Status: ${currentReport.status}
Response Time: ${currentReport.response_time}

Page Title: ${currentReport.title}
Meta Description: ${currentReport.meta_description}
H1 Headings Count: ${currentReport.h1_count}
Approximate Word Count: ${currentReport.word_count}

Total Images: ${currentReport.total_images}
Images Missing Alt: ${currentReport.images_without_alt}

Canonical URL: ${currentReport.canonical}
Robots Meta: ${currentReport.robots}
=======================================
Built for Digital Heroes Training Task
https://digitalheroesco.com
        `.trim();

        navigator.clipboard.writeText(text).then(() => {
            showToast('Report Copied', 'Summary report copied to clipboard!', 'success');
        }).catch(() => {
            showToast('Copy Failed', 'Unable to copy text to clipboard.', 'error');
        });
    });
});
