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

    data = {
        "Loan_ID": [0],
        "Gender": [int(request.form["Gender"])],
        "Married": [int(request.form["Married"])],
        "Dependents": [int(request.form["Dependents"])],
        "Education": [int(request.form["Education"])],
        "Self_Employed": [int(request.form["Self_Employed"])],
        "ApplicantIncome": [float(request.form["ApplicantIncome"])],
        "CoapplicantIncome": [float(request.form["CoapplicantIncome"])],
        "LoanAmount": [float(request.form["LoanAmount"])],
        "Loan_Amount_Term": [float(request.form["Loan_Amount_Term"])],
        "Credit_History": [float(request.form["Credit_History"])],
        "Property_Area": [int(request.form["Property_Area"])]
    }

    input_df = pd.DataFrame(data)

    input_scaled = scaler.transform(input_df)

    prediction = model.predict(input_scaled)

    result = "Loan Approved ✅" if prediction[0] == 1 else "Loan Rejected ❌"

    return render_template("submit.html", prediction=result)


if __name__ == "__main__":
    app.run(debug=True)