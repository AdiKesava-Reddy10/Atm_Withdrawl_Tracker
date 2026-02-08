import streamlit as st
import pandas as pd
import numpy as np
import re
from sklearn.ensemble import IsolationForest
import time

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="GuardVigil ATM Analyzer", layout="wide")

# FIX: Changed from st.set_page_config to st.session_state
if 'users' not in st.session_state:
    st.session_state['users'] = {} 
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

# --- 2. UTILS: VALIDATION & ML ---
def validate_password(password):
    """Checks: 6+ chars, 1 Upper, 1 Lower, 1 Number, 1 Special Char."""
    if len(password) < 6: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

@st.cache_data
def get_training_data():
    # Synthetic "Real-Time" dataset of 100 normal transactions
    data = {
        'amount': np.random.normal(60, 20, 100).tolist(),
        'hour': np.random.randint(8, 22, 100).tolist(),
        'dist': np.random.uniform(0.5, 10.0, 100).tolist()
    }
    return pd.DataFrame(data)

def train_model(data):
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(data)
    return model

# --- 3. PAGES ---
def home_page():
    st.title("🛡️ GuardVigil ATM Analyzer")
    st.subheader("Your Financial Fortress in a Digital World.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Why GuardVigil?
        * **Pulse Monitoring:** We learn your spending heartbeat.
        * **Instant Shield:** Unusual spikes are flagged in milliseconds.
        * **Travel Smart:** AI that knows when you're on vacation.
        """)
    with col2:
        st.info("**Fraud stops here.** We use advanced Isolation Forest algorithms to analyze patterns.")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("Join the Fortress (Register)", use_container_width=True):
        st.session_state['page'] = 'Register'
        st.rerun()
    if c2.button("Access Your Vault (Login)", use_container_width=True):
        st.session_state['page'] = 'Login'
        st.rerun()

def register_page():
    st.title("📝 Create Account")
    full_name = st.text_input("Full Name")
    username = st.text_input("Username")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    pwd = st.text_input("Create Password", type="password")
    pwd_confirm = st.text_input("Verify Password", type="password")
    
    st.caption("⚠️ **Constraints:** Min 6 characters, 1 Uppercase, 1 Lowercase, 1 Number, 1 Special Character.")

    if st.button("Register"):
        if not full_name or not username:
            st.error("All fields are required.")
        elif username in st.session_state['users']:
            st.error("Username already exists!")
        elif pwd != pwd_confirm:
            st.error("Passwords do not match!")
        elif not validate_password(pwd):
            st.error("Password does not meet security constraints!")
        else:
            st.session_state['users'][username] = {
                "password": pwd, "name": full_name, "cards": [], "phone": phone
            }
            st.success("Registration Successful! Please Login.")
            time.sleep(1.5)
            st.session_state['page'] = 'Login'
            st.rerun()
    
    if st.button("Back to Home"):
        st.session_state['page'] = 'Home'
        st.rerun()

def login_page():
    st.title("🔑 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if user in st.session_state['users'] and st.session_state['users'][user]['password'] == pwd:
            st.session_state['logged_in'] = True
            st.session_state['current_user'] = user
            st.session_state['page'] = 'Dashboard'
            st.rerun()
        else:
            st.error("Invalid credentials.")
    
    if st.button("Back to Home"):
        st.session_state['page'] = 'Home'
        st.rerun()

def dashboard():
    user_data = st.session_state['users'][st.session_state['current_user']]
    st.title(f"👋 Welcome, {user_data['name']}")
    
    tab1, tab2 = st.tabs(["💳 Manage Cards", "🔍 Pattern Analyzer"])
    
    with tab1:
        st.header("Add New ATM Card")
        card_type = st.selectbox("Account Type", ["Savings", "Current"])
        card_num = st.text_input("Card Number (Last 4 digits)", max_chars=4)
        if st.button("Add Card"):
            if card_num.isdigit() and len(card_num) == 4:
                user_data['cards'].append({"type": card_type, "num": card_num})
                st.success(f"{card_type} card added!")
            else:
                st.error("Please enter a valid 4-digit card number.")
            
        st.subheader("Your Linked Cards")
        if not user_data['cards']:
            st.write("No cards added yet.")
        for card in user_data['cards']:
            st.write(f"• **{card['type']}** Account (xxxx-{card['num']})")

    with tab2:
        st.header("Fraud Detection Simulator")
        st.write("Simulate a transaction to see if the AI flags it.")
        
        amt = st.number_input("Withdrawal Amount ($)", min_value=0.0, value=50.0)
        hr = st.slider("Hour of Day (24h format)", 0, 23, 14)
        dist = st.number_input("Distance from registered home (km)", min_value=0.0, value=2.0)
        
        if st.button("Verify Transaction"):
            # Load Data and Train
            train_df = get_training_data()
            model = train_model(train_df)
            
            # Predict using a DataFrame to maintain feature names
            test_point = pd.DataFrame([[amt, hr, dist]], columns=['amount', 'hour', 'dist'])
            result = model.predict(test_point)
            
            if result[0] == -1:
                st.error("🚨 ALERT: Unusual Pattern Detected! This request is outside your normal behavior.")
                st.warning(f"A security block has been placed. Contacting {user_data['phone']}...")
            else:
                st.success("✅ Transaction Verified. This matches your historical pattern.")

# --- 4. ROUTING LOGIC ---
if st.sidebar.button("Logout"):
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = None
    st.session_state['page'] = 'Home'
    st.rerun()

if st.session_state['page'] == 'Home': home_page()
elif st.session_state['page'] == 'Register': register_page()
elif st.session_state['page'] == 'Login': login_page()
elif st.session_state['page'] == 'Dashboard': 
    if st.session_state['logged_in']: dashboard()
    else: 
        st.session_state['page'] = 'Login'
        st.rerun()
