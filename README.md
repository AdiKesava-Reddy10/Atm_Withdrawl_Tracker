# 🏧 ATM Withdrawal Tracker – Secure Transaction Monitoring System

ATM Withdrawal Tracker is a Streamlit-based web application designed to monitor ATM withdrawals, manage card limits, and detect unusual transaction behavior using machine learning techniques.

The system focuses on **user security**, **fraud detection**, and **transaction history tracking**, making it suitable for academic projects and AI/ML demonstrations.

---

## 🚀 Features

### 🔐 Authentication & Security
- User Registration and Secure Login
- Strong password validation:
  - Minimum 6 characters
  - Uppercase, lowercase, number, and special character
- Forgot Password functionality using phone number verification
- Persistent user data storage using Pickle
- Account deletion option (Danger Zone)

---

### 💳 Card Management
- Link multiple ATM cards
- Supports Savings and Current accounts
- Set individual withdrawal limits for each card
- Display active linked cards with limits

---

### 🏧 Withdrawal Simulation
- Simulate ATM withdrawals
- Input:
  - Withdrawal amount
  - Distance from home
  - Time of transaction
- Automatic limit checking
- Real-time approval or rejection status

---

### 🛡️ Fraud Detection (AI/ML)
- Uses **Isolation Forest (unsupervised learning)** for anomaly detection
- Flags unusual withdrawal behavior based on:
  - Amount
  - Time of transaction
  - Distance from home
- Categorizes transactions as:
  - ✅ Approved
  - ⚠️ Flagged (Unusual Activity)
  - ❌ Failed (Over Limit)

---

### 📜 Transaction History
- Stores transaction logs with:
  - Date & time
  - Card details
  - Amount
  - Transaction status
- Displays recent transactions in a table format

---

## 🧠 Machine Learning Model
- Algorithm: Isolation Forest
- Purpose: Fraud and anomaly detection
- Training data simulated for behavioral analysis
- Easily extendable with real transaction datasets

---

## 🛠️ Tech Stack

- Frontend & Backend: Streamlit
- Programming Language: Python
- Libraries Used:
  - streamlit
  - pandas
  - numpy
  - scikit-learn
  - pickle
  - re
  - datetime
  - os

---

## 📂 Project Structure

ATM-Withdrawal-Tracker/
│
├── app.py          # Main Streamlit application
├── users_db.pkl    # Persistent user database (auto-generated)
├── README.md       # Project documentation
└── requirements.txt

---

## 📦 Installation & Setup

### 1. Clone the Repository
git clone https://github.com/your-username/ATM-Withdrawal-Tracker.git  
cd ATM-Withdrawal-Tracker

### 2. Install Dependencies
pip install streamlit pandas numpy scikit-learn

### 3. Run the Application
streamlit run app.py

The application will open automatically in your browser.

---

## 🧪 How to Use

1. Register a new user account
2. Login with your credentials
3. Link an ATM card and set a withdrawal limit
4. Simulate ATM withdrawals
5. View approval, rejection, or fraud warnings
6. Check transaction history
7. Logout or delete account if required

---

## ⚠️ Important Notes

- User data is stored locally using Pickle files
- Data persists across sessions
- No external APIs or API keys are required
- Intended for educational and demonstration purposes only

---

## 🎯 Future Enhancements

- OTP-based transaction verification
- Real-time SMS or email alerts
- Integration with real ATM datasets
- Advanced ML models for fraud detection
- Graph-based transaction analytics
- Cloud deployment

---

## 👩‍💻 Author

S.AdiKesava Reddy
AI / ML Enthusiast  
Project: ATM Withdrawal Tracker

---

## 📜 License

This project is intended strictly for educational and academic purposes.
