document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup Custom Card Options (Replacing boring dropdowns)
    const setupCardOptions = () => {
        document.querySelectorAll('.option-cards').forEach(container => {
            const cards = container.querySelectorAll('.option-card');
            const selectId = container.dataset.select;
            const targetSelect = document.getElementById(selectId);

            if (!targetSelect) return;

            // Synchronize starting value if present
            cards.forEach(card => {
                const val = card.dataset.value;
                if (targetSelect.value === val) {
                    card.classList.add('selected');
                }

                card.addEventListener('click', () => {
                    cards.forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    targetSelect.value = val;

                    // Dispatch change event
                    targetSelect.dispatchEvent(new Event('change'));
                });
            });
        });
    };

    // 2. Multi-step Form Navigation
    const setupMultiStepForm = () => {
        const sections = document.querySelectorAll('.form-section');
        const steps = document.querySelectorAll('.step-item');
        const nextBtns = document.querySelectorAll('.btn-next');
        const prevBtns = document.querySelectorAll('.btn-prev');
        let currentStep = 0;

        if (sections.length === 0) return;

        const updateFormProgress = () => {
            sections.forEach((sec, idx) => {
                if (idx === currentStep) {
                    sec.classList.add('active');
                } else {
                    sec.classList.remove('active');
                }
            });

            steps.forEach((step, idx) => {
                if (idx < currentStep) {
                    step.classList.add('completed');
                    step.classList.remove('active');
                } else if (idx === currentStep) {
                    step.classList.add('active');
                    step.classList.remove('completed');
                } else {
                    step.classList.remove('active', 'completed');
                }
            });
        };

        const validateSection = (stepIndex) => {
            const currentSection = sections[stepIndex];
            const inputs = currentSection.querySelectorAll('input[required], select[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--danger)';
                    input.addEventListener('input', function resetBorder() {
                        input.style.borderColor = '';
                        input.removeEventListener('input', resetBorder);
                    });
                }
            });

            return isValid;
        };

        nextBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (validateSection(currentStep)) {
                    if (currentStep < sections.length - 1) {
                        currentStep++;
                        updateFormProgress();
                        window.scrollTo({ top: 100, behavior: 'smooth' });
                    }
                }
            });
        });

        prevBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (currentStep > 0) {
                    currentStep--;
                    updateFormProgress();
                    window.scrollTo({ top: 100, behavior: 'smooth' });
                }
            });
        });

        updateFormProgress();
    };

    // 3. AJAX Submission & Beautiful Loader
    const setupFormSubmission = () => {
        const form = document.getElementById('predictor-form');
        const loader = document.getElementById('loading-overlay');
        const loaderStatus = document.getElementById('loader-status');
        const resultSection = document.getElementById('result-section');
        const formWrapper = document.getElementById('form-wrapper');

        if (!form || !loader) return;

        const statuses = [
            { text: "Structuring applicant features...", delay: 600 },
            { text: "Scaling numerical parameters...", delay: 800 },
            { text: "Evaluating risk indexes...", delay: 700 },
            { text: "Consulting decision tree models...", delay: 600 },
            { text: "Generating eligibility report...", delay: 400 }
        ];

        const runLoadingAnimations = async () => {
            loader.classList.add('active');
            for (let status of statuses) {
                loaderStatus.textContent = status.text;
                await new Promise(resolve => setTimeout(resolve, status.delay));
            }
        };

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Run validation check
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--danger)';
                }
            });

            if (!isValid) return;

            // Trigger beautiful loader
            await runLoadingAnimations();

            const formData = new FormData(form);

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const data = await response.json();

                // Hide loader
                loader.classList.remove('active');

                if (data.status === 'success') {
                    // Inject result and show result section
                    renderPredictionResult(data);
                } else {
                    alert('Prediction failed: ' + (data.message || 'Unknown error'));
                }
            } catch (err) {
                loader.classList.remove('active');
                console.error(err);
                alert('An error occurred during prediction.');
            }
        });
    };

    // 4. Render prediction result
    const renderPredictionResult = (data) => {
        const formWrapper   = document.getElementById('form-wrapper');
        const resultSection = document.getElementById('result-section');
        if (!formWrapper || !resultSection) return;

        const isApproved = data.approved;
        const rec        = data.recommendation || null;
        const tips       = data.tips || [];

        const applicantIncome = parseFloat(document.getElementById('ApplicantIncome').value) || 0;
        const loanAmount      = parseFloat(document.getElementById('LoanAmount').value)      || 0;
        const creditHistory   = document.getElementById('Credit_History').value;

        const fmt = (n) => Math.round(n).toLocaleString('en-IN');

        const approvedSVG = `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>`;
        const rejectedSVG = `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`;

        // ── APPROVED: clean summary ───────────────────────────────────────────
        let bodyHTML = '';
        if (isApproved && rec) {
            const riskCls = rec.risk_level === 'Low' ? 'low' : rec.risk_level === 'Medium' ? 'medium' : 'high';
            bodyHTML = `
                <div class="summary-metrics" style="margin-top:1.5rem">
                    <div class="summary-item">
                        <span class="summary-label">Your Monthly Income</span>
                        <span class="summary-value">₹${fmt(applicantIncome)}/mo</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">You Requested</span>
                        <span class="summary-value">₹${fmt(loanAmount)}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Max Eligible Loan</span>
                        <span class="summary-value text-success">₹${fmt(rec.recommended_loan)}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Monthly EMI</span>
                        <span class="summary-value text-accent">₹${fmt(rec.suggested_emi)}/mo</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Interest Rate / Tenure</span>
                        <span class="summary-value">${rec.interest_rate}% p.a. · ${rec.tenure_years} Years</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">EMI-to-Income · Risk</span>
                        <span class="summary-value">${rec.emi_to_income_ratio}% · <span class="risk-badge ${riskCls}">${rec.risk_level}</span></span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Credit History</span>
                        <span class="summary-value ${creditHistory === '1' ? 'text-success' : 'text-danger'}">
                            ${creditHistory === '1' ? 'Good' : 'Poor'}
                        </span>
                    </div>
                </div>`;
        }

        // ── REJECTED: show actual numbers + tips ──────────────────────────────
        if (!isApproved && rec) {
            const tipItems = tips.map(t =>
                `<li><span class="suggestion-dot">›</span><span>${t}</span></li>`
            ).join('');

            bodyHTML = `
                <div class="rejection-box">
                    <p class="box-heading">Your Financial Snapshot</p>
                    <div class="summary-metrics">
                        <div class="summary-item">
                            <span class="summary-label">Your Monthly Income</span>
                            <span class="summary-value">₹${fmt(rec.total_income)}/mo</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">You Requested</span>
                            <span class="summary-value text-danger">₹${fmt(loanAmount)}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Max You Can Get</span>
                            <span class="summary-value text-success">₹${fmt(rec.recommended_loan)}</span>
                        </div>
                        ${rec.shortfall > 0 ? `
                        <div class="summary-item">
                            <span class="summary-label">Reduce Loan By</span>
                            <span class="summary-value text-danger">₹${fmt(rec.shortfall)}</span>
                        </div>` : ''}
                        <div class="summary-item">
                            <span class="summary-label">Affordable EMI</span>
                            <span class="summary-value text-accent">₹${fmt(rec.suggested_emi)}/mo</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Credit History</span>
                            <span class="summary-value ${creditHistory === '1' ? 'text-success' : 'text-danger'}">
                                ${creditHistory === '1' ? 'Good' : 'Poor'}
                            </span>
                        </div>
                    </div>
                    ${tipItems.length > 0 ? `
                    <div class="result-divider"></div>
                    <p class="box-heading">How to Improve Eligibility</p>
                    <ul class="suggestion-list">${tipItems}</ul>` : ''}
                </div>`;
        }

        // ── Assemble card ─────────────────────────────────────────────────────
        resultSection.innerHTML = `
            <div class="glass-card result-container" style="animation: fadeIn 0.6s ease-in-out forwards;">

                <div class="result-badge ${isApproved ? 'approved' : 'rejected'}">
                    ${isApproved ? approvedSVG : rejectedSVG}
                </div>

                <h1 class="result-title ${isApproved ? 'approved' : 'rejected'}">
                    ${isApproved ? 'Loan Approved' : 'Loan Rejected'}
                </h1>

                <p class="result-text">
                    ${isApproved
                        ? 'Congratulations! Based on your financial profile you are eligible. Here is your loan summary.'
                        : 'Your application could not be approved at this time. Here is what we found.'
                    }
                </p>

                ${bodyHTML}

                <div style="display:flex; justify-content:center; gap:1rem; margin-top:2rem;">
                    <button class="btn btn-primary" onclick="window.location.reload();">
                        <svg style="width:18px;height:18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.253 8H18"></path></svg>
                        New Evaluation
                    </button>
                    <a href="/" class="btn btn-secondary">
                        <svg style="width:18px;height:18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                        Home Dashboard
                    </a>
                </div>

            </div>`;

        formWrapper.style.display = 'none';
        resultSection.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Execute functions
    setupCardOptions();
    setupMultiStepForm();
    setupFormSubmission();
});
