import streamlit as st
import pandas as pd
import numpy as np
import re
from sklearn.ensemble import IsolationForest
import time

# --- CONFIG & SESSION STATE ---
st.set_page_config(page_title="GuardVigil ATM Analyzer", layout="wide")

if 'users' not in st.set_page_config:
    st.session_state['users'] = {} # Simple in-memory DB: {username: {password, full_name, cards: []}}
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# --- UTILS: VALIDATION & ML ---
def validate_password(password):
    if len(password) < 6: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

@st.cache_data
def get_training_data():
    # Creating a synthetic "Real-Time" dataset of 100 normal transactions
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

# --- PAGES ---
def home_page():
    st.title("🛡️ GuardVigil ATM Analyzer")
    st.subheader("Your Financial Fortress in a Digital World.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Why GuardVigil?
        * **Pulse Monitoring:** We learn your spending heartbeat.
        * **Instant Shield:** Unusual spikes are flagged in milliseconds.
        * **Travel Smart:** Our AI distinguishes between a vacation and a heist.
        """)
    with col2:
        st.info("**" + "Fraud stops here." + "** We use advanced Isolation Forest algorithms to ensure your hard-earned money stays exactly where it belongs.")

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
    
    st.caption("Constraint: Min 6 chars, 1 Uppercase, 1 Lowercase, 1 Number, 1 Special Char.")

    if st.button("Register"):
        if username in st.session_state['users']:
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
            time.sleep(1)
            st.session_state['page'] = 'Login'
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

def dashboard():
    user_data = st.session_state['users'][st.session_state['current_user']]
    st.title(f"👋 Welcome, {user_data['name']}")
    
    tab1, tab2 = st.tabs(["💳 Manage Cards", "🔍 Pattern Analyzer"])
    
    with tab1:
        st.header("Add New ATM Card")
        card_type = st.selectbox("Account Type", ["Savings", "Current"])
        card_num = st.text_input("Card Number (Last 4 digits)")
        if st.button("Add Card"):
            user_data['cards'].append({"type": card_type, "num": card_num})
            st.success(f"{card_type} card added!")
            
        st.subheader("Your Cards")
        for card in user_data['cards']:
            st.write(f"• **{card['type']}** Account ending in {card['num']}")

    with tab2:
        st.header("Real-Time Transaction Check")
        st.write("Simulate a withdrawal to test the Fraud Analyzer.")
        
        amt = st.number_input("Withdrawal Amount ($)", min_value=0)
        hr = st.slider("Hour of Day (24h)", 0, 23, 12)
        dist = st.number_input("Distance from Home (km)", min_value=0.0)
        
        if st.button("Analyze Transaction"):
            # Load Data and Train
            train_df = get_training_data()
            model = train_model(train_df)
            
            # Predict
            result = model.predict([[amt, hr, dist]])
            
            if result[0] == -1:
                st.error("🚨 ALERT: Unusual Pattern Detected! This transaction deviates from your typical behavior.")
                st.warning("A verification code has been sent to " + user_data['phone'])
            else:
                st.success("✅ Transaction Verified. This matches your historical withdrawal pattern.")

# --- ROUTING ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

if st.session_state['page'] == 'Home': home_page()
elif st.session_state['page'] == 'Register': register_page()
elif st.session_state['page'] == 'Login': login_page()
elif st.session_state['page'] == 'Dashboard': dashboard()

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
