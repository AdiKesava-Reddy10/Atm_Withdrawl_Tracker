import streamlit as st
import pandas as pd
import numpy as np
import re
import pickle
import os
import time
from datetime import datetime
from sklearn.ensemble import IsolationForest

# --- 1. DATA PERSISTENCE ---
DB_FILE = "users_db.pkl"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                return pickle.load(f)
        except:
            return {}
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
    if not (re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and 
            re.search(r"[0-9]", password) and re.search(r"[!@#$%^&*()]", password)):
        return False
    return True

@st.cache_data
def get_training_data():
    data = {'amount': np.random.normal(60, 20, 100).tolist(),
            'hour': np.random.randint(8, 22, 100).tolist(),
            'dist': np.random.uniform(0.5, 10.0, 100).tolist()}
    return pd.DataFrame(data)

# --- 4. PAGES ---
def home_page():
    st.title("🛡️ GuardVigil ATM Analyzer")
    st.markdown("### *Your Security, Personalized.*")
    st.info("Advanced behavioral analysis to protect your ATM transactions.")
    col1, col2 = st.columns(2)
    if col1.button("Register New User", use_container_width=True):
        st.session_state['page'] = 'Register'; st.rerun()
    if col2.button("Login to Dashboard", use_container_width=True):
        st.session_state['page'] = 'Login'; st.rerun()

def register_page():
    st.title("📝 User Registration")
    fn = st.text_input("Full Name")
    un = st.text_input("Username")
    ph = st.text_input("Phone Number")
    pw = st.text_input("Create Password", type="password")
    
    if st.button("Register", use_container_width=True):
        if un in st.session_state['users']: st.error("Username already taken!")
        elif validate_password(pw):
            st.session_state['users'][un] = {
                "password": pw, "name": fn, "phone": ph, "cards": [], "history": []
            }
            save_users(st.session_state['users'])
            st.success("Account created successfully!"); st.session_state['page'] = 'Login'; st.rerun()
        else: st.error("Password must be 6+ chars with Upper, Lower, Number, and Special char.")
    
    st.write("---")
    # REDIRECT TO LOGIN
    st.write("Already have an account?")
    if st.button("Login Here"):
        st.session_state['page'] = 'Login'
        st.rerun()

def login_page():
    st.title("🔓 Secure Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", use_container_width=True):
            users = st.session_state['users']
            if u in users and users[u]['password'] == p:
                st.session_state['logged_in'], st.session_state['current_user'] = True, u
                st.session_state['page'] = 'Dashboard'; st.rerun()
            else: st.error("Invalid credentials.")
    with col2:
        if st.button("Forgot Password?", use_container_width=True):
            st.session_state['page'] = 'Forgot'; st.rerun()
    
    st.write("---")
    # REDIRECT TO REGISTRATION
    st.write("New to GuardVigil?")
    if st.button("Create an Account"):
        st.session_state['page'] = 'Register'
        st.rerun()

def forgot_password_page():
    st.title("🔑 Reset Password")
    u = st.text_input("Username")
    ph = st.text_input("Phone Number")
    npw = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        if u in st.session_state['users'] and st.session_state['users'][u]['phone'] == ph:
            if validate_password(npw):
                st.session_state['users'][u]['password'] = npw
                save_users(st.session_state['users'])
                st.success("Password updated!"); st.session_state['page'] = 'Login'; st.rerun()
            else: st.error("New password is too weak.")
        else: st.error("Details do not match.")
    if st.button("Back to Login"):
        st.session_state['page'] = 'Login'; st.rerun()

def dashboard():
    user = st.session_state['current_user']
    user_data = st.session_state['users'][user]
    st.title(f"Welcome, {user_data['name']}")
    
    tab1, tab2, tab3 = st.tabs(["💳 Card Management", "🛡️ Fraud Analysis", "📜 History"])
    
    with tab1:
        st.subheader("Link a New Card")
        c_type = st.selectbox("Account Type", ["Savings", "Current"])
        c_num = st.text_input("Last 4 Digits", max_chars=4)
        c_limit = st.number_input("Set Withdrawal Limit ($)", min_value=1, value=500)
        
        if st.button("Save Card"):
            user_data['cards'].append({"type": c_type, "num": c_num, "limit": c_limit})
            save_users(st.session_state['users'])
            st.success(f"Card Linked with ${c_limit} limit.")
        
        st.divider()
        st.subheader("Your Active Cards")
        for c in user_data['cards']:
            limit_display = c.get('limit', "Unset")
            st.write(f"✅ {c['type']} (xxxx-{c['num']}) | Limit: **${limit_display}**")

    with tab2:
        st.header("Withdrawal Simulator")
        if not user_data['cards']:
            st.warning("Please add a card in Management first.")
        else:
            options = [f"{c['type']} (xxxx-{c['num']})" for c in user_data['cards']]
            sel = st.selectbox("Select Card", options=options)
            card = next(i for i in user_data['cards'] if f"{i['type']} (xxxx-{i['num']})" == sel)
            
            amt = st.number_input("Withdrawal Amount ($)", value=50)
            dist = st.number_input("Distance from Home (km)", value=5)
            hr = st.slider("Hour (0-23)", 0, 23, 12)
            
            if st.button("Run Analysis"):
                status = ""
                card_limit = card.get('limit', 999999) 
                
                if amt > card_limit:
                    status = f"FAILED: Over Limit (${card_limit})"
                    st.error(f"❌ {status}")
                else:
                    model = IsolationForest(contamination=0.05).fit(get_training_data())
                    test_point = pd.DataFrame([[amt, hr, dist]], columns=['amount', 'hour', 'dist'])
                    pred = model.predict(test_point)
                    if pred[0] == -1:
                        status = "FLAGGED: Unusual Activity"
                        st.warning(f"⚠️ {status}")
                    else:
                        status = "APPROVED"
                        st.success(f"✅ {status}")
                
                if 'history' not in user_data: user_data['history'] = []
                user_data['history'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "card": sel, "amount": amt, "status": status
                })
                save_users(st.session_state['users'])

    with tab3:
        st.header("Transaction Log")
        history = user_data.get('history', [])
        if history:
            st.table(pd.DataFrame(history).iloc[::-1])
        else:
            st.write("No history found.")

# --- 5. SIDEBAR & DELETE ACCOUNT ---
with st.sidebar:
    st.header("Account Settings")
    if st.session_state['logged_in']:
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.session_state['page'] = 'Home'; st.rerun()
        
        st.divider()
        st.subheader("Danger Zone")
        if st.button("❌ Delete My Account"):
            curr_user = st.session_state['current_user']
            del st.session_state['users'][curr_user]
            save_users(st.session_state['users'])
            st.session_state['logged_in'] = False
            st.session_state['page'] = 'Home'
            st.warning("Account deleted permanently.")
            time.sleep(1)
            st.rerun()
    else:
        st.write("Log in to access settings.")

# --- 6. ROUTING ---
if st.session_state['page'] == 'Home': home_page()
elif st.session_state['page'] == 'Register': register_page()
elif st.session_state['page'] == 'Login': login_page()
elif st.session_state['page'] == 'Forgot': forgot_password_page()
elif st.session_state['page'] == 'Dashboard': 
    if st.session_state['logged_in']: dashboard()
    else: st.session_state['page'] = 'Login'; st.rerun()
