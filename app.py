import streamlit as st
import pandas as pd
import numpy as np
import re
import pickle
import os
from sklearn.ensemble import IsolationForest

# --- 1. DATA PERSISTENCE (Local Database) ---
DB_FILE = "users_db.pkl"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "wb") as f:
        pickle.dump(users, f)

# --- 2. CONFIG & SESSION STATE ---
st.set_page_config(page_title="GuardVigil ATM Analyzer", layout="wide")

if 'users' not in st.session_state:
    st.session_state['users'] = load_users()
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

# --- 3. UTILS ---
def validate_password(password):
    if len(password) < 6: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True

@st.cache_data
def get_training_data():
    data = {
        'amount': np.random.normal(60, 20, 100).tolist(),
        'hour': np.random.randint(8, 22, 100).tolist(),
        'dist': np.random.uniform(0.5, 10.0, 100).tolist()
    }
    return pd.DataFrame(data)

# --- 4. PAGES ---
def home_page():
    st.title("🛡️ GuardVigil ATM Analyzer")
    st.markdown("### *Your patterns protect you.*")
    
    st.info("Our AI uses **Isolation Forest** algorithms to detect if a withdrawal matches your historical behavior.")
    
    col1, col2 = st.columns(2)
    if col1.button("Register New Account", use_container_width=True):
        st.session_state['page'] = 'Register'
        st.rerun()
    if col2.button("Login to Vault", use_container_width=True):
        st.session_state['page'] = 'Login'
        st.rerun()

def register_page():
    st.title("📝 User Registration")
    full_name = st.text_input("Full Name")
    username = st.text_input("Username")
    phone = st.text_input("Phone Number")
    pwd = st.text_input("Create Password", type="password")
    pwd_confirm = st.text_input("Verify Password", type="password")
    
    if st.button("Complete Registration"):
        if username in st.session_state['users']:
            st.error("Username already exists!")
        elif pwd != pwd_confirm:
            st.error("Passwords do not match!")
        elif not validate_password(pwd):
            st.error("Security Requirements: 6+ chars, 1 Upper, 1 Lower, 1 Number, 1 Special.")
        else:
            # Add to state and Save to Disk
            st.session_state['users'][username] = {
                "password": pwd, "name": full_name, "phone": phone, "cards": []
            }
            save_users(st.session_state['users'])
            st.success("Account Created! You can now log in anytime.")
            st.session_state['page'] = 'Login'
            st.rerun()
    
    if st.button("Back"): st.session_state['page'] = 'Home'; st.rerun()

def forgot_password_page():
    st.title("🔑 Reset Password")
    user = st.text_input("Enter Username")
    phone = st.text_input("Enter Registered Phone Number")
    new_pwd = st.text_input("New Password", type="password")
    
    if st.button("Update Password"):
        users = st.session_state['users']
        if user in users and users[user]['phone'] == phone:
            if validate_password(new_pwd):
                users[user]['password'] = new_pwd
                save_users(users)
                st.success("Password updated successfully!")
                st.session_state['page'] = 'Login'
                st.rerun()
            else:
                st.error("New password doesn't meet security constraints.")
        else:
            st.error("Username and Phone number do not match our records.")
    
    if st.button("Back to Login"): st.session_state['page'] = 'Login'; st.rerun()

def login_page():
    st.title("🔓 Secure Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Login"):
        users = st.session_state['users']
        if user in users and users[user]['password'] == pwd:
            st.session_state['logged_in'] = True
            st.session_state['current_user'] = user
            st.session_state['page'] = 'Dashboard'
            st.rerun()
        else:
            st.error("Invalid Username or Password.")
            
    if st.button("Forgot Password?"):
        st.session_state['page'] = 'Forgot'
        st.rerun()

def dashboard():
    user = st.session_state['current_user']
    user_data = st.session_state['users'][user]
    st.title(f"Welcome back, {user_data['name']}!")
    
    tab1, tab2 = st.tabs(["💳 Card Management", "🛡️ Fraud Analysis"])
    
    with tab1:
        st.subheader("Link a Card")
        c_type = st.selectbox("Type", ["Savings", "Current"])
        c_num = st.text_input("Last 4 Digits", max_chars=4)
        if st.button("Save Card"):
            user_data['cards'].append({"type": c_type, "num": c_num})
            save_users(st.session_state['users']) # Save card to disk
            st.success("Card added to your persistent profile.")
        
        for c in user_data['cards']:
            st.write(f"✅ {c['type']} Card (xxxx-{c['num']})")

    with tab2:
        st.header("Test Withdrawal Pattern")
        amt = st.number_input("Amount ($)", value=50)
        dist = st.number_input("Distance (km)", value=5)
        hr = st.slider("Hour", 0, 23, 12)
        
        if st.button("Run Security Check"):
            model = IsolationForest(contamination=0.05).fit(get_training_data())
            pred = model.predict(pd.DataFrame([[amt, hr, dist]], columns=['amount', 'hour', 'dist']))
            if pred[0] == -1:
                st.error("Fraud Alert! This pattern is unusual for your account.")
            else:
                st.success("Pattern recognized. Transaction Safe.")

# --- 5. NAVIGATION ---
if st.sidebar.button("Log Out"):
    st.session_state['logged_in'] = False
    st.session_state['page'] = 'Home'
    st.rerun()

if st.session_state['page'] == 'Home': home_page()
elif st.session_state['page'] == 'Register': register_page()
elif st.session_state['page'] == 'Login': login_page()
elif st.session_state['page'] == 'Forgot': forgot_password_page()
elif st.session_state['page'] == 'Dashboard': dashboard()
