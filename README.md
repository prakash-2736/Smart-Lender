# SmartLender™ AI - Loan Eligibility & Recommendation System

SmartLender™ is a premium, deployment-ready Flask web application integrated with an optimized machine learning pipeline to predict loan approvals and recommend financial terms. The interface is built with modern **glassmorphism** styling (dark navy theme) and features smooth micro-animations.

---

## 🌟 Key Features

1. **Robust Machine Learning Engine**
   - Implements an optimized **Random Forest Classifier** achieving **81.07% test accuracy** (up from 79.3%).
   - Retrained to drop the unnecessary `Loan_ID` column, ensuring predictions depend purely on real financial factors.
   - Correctly handles class imbalances with **SMOTE** oversampling and normalizes features using `StandardScaler`.

2. **Advanced Financial Recommendation Engine**
   - **When Approved:** Dynamically calculates your **Maximum Eligible Loan Amount** and **Estimated Monthly EMI** using standard amortization mathematics. Displays tenure (in years), interest rate (fixed at 8.5% p.a.), EMI-to-Income ratio, and a calculated Risk Level (Low/Medium/High).
   - **When Rejected:** Displays a calculated financial snapshot showing your affordable metrics, how much to reduce your requested loan by (shortfall), and lists smart contextual suggestions to improve eligibility (e.g., adding a co-applicant, improving credit score).

3. **Premium Banking Dashboard UI**
   - High-fidelity glassmorphic dark mode layout with responsive elements.
   - Re-designed results interface designed to fit completely on one screen (no unnecessary vertical scrolling on standard laptops).
   - Multi-step form with validation, progress indicator, and custom interactive option cards.

---

## 📁 Repository Structure

```
Smart-Lender/
├── app.py                      # Flask backend application
├── requirements.txt            # Python dependencies (scikit-learn, Flask, pandas, etc.)
├── .gitignore                  # Excludes venv, logs, __pycache__
├── README.md                   # Project documentation
├── dataset/
│   └── loan_prediction.csv     # Training source dataset
├── model/
│   ├── loan_model.pkl          # Trained Random Forest classifier
│   ├── scaler.pkl              # Fitted StandardScaler instance
│   └── feature_columns.pkl     # Reference for exact feature sequence order
├── notebook/
│   └── Smart_Lender.ipynb      # Exploration and original pipeline notebook
├── static/
│   ├── css/
│   │   └── style.css           # Modern CSS styling (glassmorphism theme)
│   └── js/
│       └── main.js             # Form navigation, AJAX submission, dynamic rendering
└── templates/
    ├── home.html               # Welcome dashboard page
    ├── predict.html            # Multi-step prediction form
    └── submit.html             # Fallback result page (non-AJAX)
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Installation
Clone the repository and set up a virtual environment:
```bash
# Clone the repository
git clone https://github.com/yourusername/Smart-Lender.git
cd Smart-Lender

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
Start the Flask development server:
```bash
python3 app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📊 Model Pipeline Details

The machine learning pipeline consists of:
1. **Imputation:**
   - Categorical columns (Gender, Married, Dependents, Self_Employed, Credit_History) are imputed with their **mode**.
   - Numerical columns (LoanAmount, Loan_Amount_Term) are imputed with their **mean**.
2. **Encoding:** Consistent Label Encoding mapped across:
   - `Gender`: Female = 0, Male = 1
   - `Married`: No = 0, Yes = 1
   - `Dependents`: 0 = 0, 1 = 1, 2 = 2, 3+ = 3
   - `Education`: Graduate = 0, Not Graduate = 1
   - `Self_Employed`: No = 0, Yes = 1
   - `Property_Area`: Rural = 0, Semiurban = 1, Urban = 2
3. **Balancing & Scaling:** SMOTE (Synthetic Minority Over-sampling Technique) to balance target variables, followed by standard scaling (`StandardScaler`).

---

## 🛠️ Deployment

This project is configured and ready to be deployed directly to platform-as-a-service providers like **Render** or **Heroku**:
- Uses `gunicorn` for a production-grade WSGI server interface.
- Scaler and classification artifacts are serialized via `joblib` for rapid inference response times (<50ms).
- Fully responsive on all device viewports (desktop, tablet, and mobile screens).
