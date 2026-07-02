from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

model = joblib.load("model/loan_model.pkl")
scaler = joblib.load("model/scaler.pkl")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predict")
def predict_page():
    return render_template("predict.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Convert raw INR inputs to the model's training scale (USD-like numbers)
        # Income in INR (e.g. 50,000) / 10 -> 5,000 (typical training scale)
        # Loan Amount in INR (e.g. 15,00,000) / 10,000 -> 150 (typical training scale)
        raw_app_income = float(request.form.get("ApplicantIncome", 0.0))
        raw_coapp_income = float(request.form.get("CoapplicantIncome", 0.0))
        raw_loan_amount = float(request.form.get("LoanAmount", 0.0))

        scaled_app_income = raw_app_income / 10.0
        scaled_coapp_income = raw_coapp_income / 10.0
        scaled_loan_amount = raw_loan_amount / 10000.0

        data = {
            "Loan_ID": [0],
            "Gender": [int(request.form.get("Gender", 1))],
            "Married": [int(request.form.get("Married", 0))],
            "Dependents": [int(request.form.get("Dependents", 0))],
            "Education": [int(request.form.get("Education", 0))],
            "Self_Employed": [int(request.form.get("Self_Employed", 0))],
            "ApplicantIncome": [scaled_app_income],
            "CoapplicantIncome": [scaled_coapp_income],
            "LoanAmount": [scaled_loan_amount],
            "Loan_Amount_Term": [float(request.form.get("Loan_Amount_Term", 360.0))],
            "Credit_History": [float(request.form.get("Credit_History", 1.0))],
            "Property_Area": [int(request.form.get("Property_Area", 0))]
        }

        input_df = pd.DataFrame(data)
        input_scaled = scaler.transform(input_df)
        prediction = model.predict(input_scaled)
        
        result_text = "Loan Approved" if prediction[0] == 1 else "Loan Rejected"
        is_approved = bool(prediction[0] == 1)
        
        # Check if the request is an AJAX/JSON request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("json") == "1":
            return {
                "status": "success",
                "prediction": result_text,
                "approved": is_approved
            }

        return render_template("submit.html", prediction=result_text + (" ✅" if is_approved else " ❌"), approved=is_approved)
    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("json") == "1":
            return {"status": "error", "message": str(e)}, 400
        return f"An error occurred: {str(e)}", 400


if __name__ == "__main__":
    app.run(debug=True)