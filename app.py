from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# ── Load trained artifacts ────────────────────────────────────────────────────
model           = joblib.load("model/loan_model.pkl")
scaler          = joblib.load("model/scaler.pkl")
FEATURE_COLUMNS = joblib.load("model/feature_columns.pkl")
# ['Gender','Married','Dependents','Education','Self_Employed',
#  'ApplicantIncome','CoapplicantIncome','LoanAmount',
#  'Loan_Amount_Term','Credit_History','Property_Area']

# Label encoding reference (from training — LabelEncoder alphabetical order):
#   Gender:        Female=0, Male=1
#   Married:       No=0, Yes=1
#   Dependents:    0=0, 1=1, 2=2, 3+=3
#   Education:     Graduate=0, Not Graduate=1
#   Self_Employed: No=0, Yes=1
#   Property_Area: Rural=0, Semiurban=1, Urban=2
#   Credit_History: 0.0=0, 1.0=1


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predict")
def predict_page():
    return render_template("predict.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # ── Parse form values ─────────────────────────────────────────────────
        # Income inputs arrive as raw Rupees (e.g. 50000).
        # The training dataset used income in the same raw unit (e.g. 5849),
        # so we divide by 10 to convert INR scale → dataset scale.
        # LoanAmount in training was in thousands (e.g. 128.0).
        # Users enter full Rupees (e.g. 1280000), so we divide by 10000.
        raw_applicant_income  = float(request.form.get("ApplicantIncome",  0))
        raw_coapplicant_income = float(request.form.get("CoapplicantIncome", 0))
        raw_loan_amount        = float(request.form.get("LoanAmount",       0))

        data = {
            "Gender":            [int(request.form.get("Gender",         1))],
            "Married":           [int(request.form.get("Married",        0))],
            "Dependents":        [int(request.form.get("Dependents",     0))],
            "Education":         [int(request.form.get("Education",      0))],
            "Self_Employed":     [int(request.form.get("Self_Employed",  0))],
            "ApplicantIncome":   [raw_applicant_income  / 10.0],
            "CoapplicantIncome": [raw_coapplicant_income / 10.0],
            "LoanAmount":        [raw_loan_amount        / 10000.0],
            "Loan_Amount_Term":  [float(request.form.get("Loan_Amount_Term", 360))],
            "Credit_History":    [float(request.form.get("Credit_History",   1))],
            "Property_Area":     [int(request.form.get("Property_Area",   0))],
        }

        # ── Build DataFrame in the exact column order used during training ────
        input_df     = pd.DataFrame(data, columns=FEATURE_COLUMNS)
        input_scaled = scaler.transform(input_df)
        prediction   = model.predict(input_scaled)

        is_approved = bool(prediction[0] == 1)
        result_text = "Loan Approved" if is_approved else "Loan Rejected"

        # ── AJAX response (used by main.js) ───────────────────────────────────
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "status":    "success",
                "prediction": result_text,
                "approved":   is_approved,
            })

        # ── Regular form post → submit.html ───────────────────────────────────
        emoji = " ✅" if is_approved else " ❌"
        return render_template("submit.html",
                               prediction=result_text + emoji,
                               approved=is_approved)

    except Exception as exc:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": str(exc)}), 400
        return f"An error occurred: {exc}", 400


if __name__ == "__main__":
    app.run(debug=True)