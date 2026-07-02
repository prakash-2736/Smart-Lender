from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import math

app = Flask(__name__)

# ── Load trained artifacts ────────────────────────────────────────────────────
model           = joblib.load("model/loan_model.pkl")
scaler          = joblib.load("model/scaler.pkl")
FEATURE_COLUMNS = joblib.load("model/feature_columns.pkl")

ANNUAL_RATE   = 8.5      # % per annum (default interest rate)
MAX_EMI_RATIO = 0.40     # 40% of total income as max EMI


# ── Loan Recommendation Helper ────────────────────────────────────────────────

def calculate_recommendation(applicant_income, coapplicant_income,
                              loan_term_months, credit_history, requested_loan):
    """
    Calculate the maximum affordable loan, EMI, and risk metrics.
    Always computed — used for BOTH approved and rejected results.
    All amounts in Indian Rupees.
    """
    total_income   = applicant_income + coapplicant_income
    monthly_rate   = ANNUAL_RATE / 12 / 100
    n              = int(loan_term_months)
    tenure_years   = round(n / 12)

    if total_income <= 0 or monthly_rate <= 0 or n <= 0:
        return None

    compound = math.pow(1 + monthly_rate, n)

    # Maximum EMI the applicant can afford (40% of total income)
    max_emi = MAX_EMI_RATIO * total_income

    # Maximum principal from EMI formula:  P = EMI × ((1+r)^n − 1) / (r × (1+r)^n)
    recommended_loan = max_emi * (compound - 1) / (monthly_rate * compound)
    recommended_loan = round(recommended_loan / 1000) * 1000

    # EMI for the recommended loan
    suggested_emi = round(recommended_loan * monthly_rate * compound / (compound - 1))

    # EMI for the requested loan
    if requested_loan > 0:
        requested_emi = requested_loan * monthly_rate * compound / (compound - 1)
        emi_ratio     = round((requested_emi / total_income) * 100, 1)
    else:
        requested_emi = 0
        emi_ratio     = 0.0

    # How much to reduce
    shortfall = max(0, int(requested_loan - recommended_loan))

    # Risk level
    if credit_history == 1 and emi_ratio < 30:
        risk = "Low"
    elif credit_history == 1 and emi_ratio <= 40:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "recommended_loan":    int(recommended_loan),
        "suggested_emi":       int(suggested_emi),
        "requested_emi":       int(round(requested_emi)),
        "interest_rate":       ANNUAL_RATE,
        "tenure_months":       n,
        "tenure_years":        tenure_years,
        "emi_to_income_ratio": emi_ratio,
        "risk_level":          risk,
        "total_income":        int(total_income),
        "applicant_income":    int(applicant_income),
        "coapplicant_income":  int(coapplicant_income),
        "requested_loan":      int(requested_loan),
        "shortfall":           shortfall,
    }


def get_rejection_tips(credit_history, coapplicant_income, loan_term_months):
    """Short contextual tips based on the applicant's profile gaps."""
    tips = []
    if credit_history == 0:
        tips.append("Improve credit history by clearing existing dues on time")
    if coapplicant_income == 0:
        tips.append("Add a co-applicant to boost combined monthly income")
    if int(loan_term_months) < 360:
        tips.append("Consider a longer tenure (e.g., 30 years) to lower monthly EMI")
    tips.append("Maintain clean repayment record for 6 months before reapplying")
    return tips


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predict")
def predict_page():
    return render_template("predict.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # ── Parse raw INR values ──────────────────────────────────────────────
        raw_applicant_income   = float(request.form.get("ApplicantIncome",   0))
        raw_coapplicant_income = float(request.form.get("CoapplicantIncome", 0))
        raw_loan_amount        = float(request.form.get("LoanAmount",        0))
        loan_amount_term       = float(request.form.get("Loan_Amount_Term",  360))
        credit_history         = int(request.form.get("Credit_History",      1))

        # ── Scale for model ───────────────────────────────────────────────────
        data = {
            "Gender":            [int(request.form.get("Gender",        1))],
            "Married":           [int(request.form.get("Married",       0))],
            "Dependents":        [int(request.form.get("Dependents",    0))],
            "Education":         [int(request.form.get("Education",     0))],
            "Self_Employed":     [int(request.form.get("Self_Employed", 0))],
            "ApplicantIncome":   [raw_applicant_income   / 10.0],
            "CoapplicantIncome": [raw_coapplicant_income / 10.0],
            "LoanAmount":        [raw_loan_amount        / 10000.0],
            "Loan_Amount_Term":  [loan_amount_term],
            "Credit_History":    [float(credit_history)],
            "Property_Area":     [int(request.form.get("Property_Area", 0))],
        }

        input_df     = pd.DataFrame(data, columns=FEATURE_COLUMNS)
        input_scaled = scaler.transform(input_df)
        prediction   = model.predict(input_scaled)

        is_approved = bool(prediction[0] == 1)
        result_text = "Loan Approved" if is_approved else "Loan Rejected"

        # ── Always calculate recommendation ───────────────────────────────────
        rec = calculate_recommendation(
                raw_applicant_income, raw_coapplicant_income,
                loan_amount_term, credit_history, raw_loan_amount)

        tips = [] if is_approved else get_rejection_tips(
                credit_history, raw_coapplicant_income, loan_amount_term)

        # ── AJAX response ─────────────────────────────────────────────────────
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "status":         "success",
                "prediction":     result_text,
                "approved":       is_approved,
                "recommendation": rec,
                "tips":           tips,
            })

        # ── Regular POST → submit.html ────────────────────────────────────────
        emoji = " ✅" if is_approved else " ❌"
        return render_template(
            "submit.html",
            prediction=result_text + emoji,
            approved=is_approved,
            rec=rec,
            tips=tips,
            applicant_income=int(raw_applicant_income),
            requested_loan=int(raw_loan_amount),
            credit_history=credit_history,
        )

    except Exception as exc:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": str(exc)}), 400
        return f"An error occurred: {exc}", 400


if __name__ == "__main__":
    app.run(debug=True)