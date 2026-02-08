import streamlit as st
import pandas as pd
import numpy as np
import re
import pickle
import os
from datetime import datetime
from sklearn.ensemble import IsolationForest

# --- 1. DATA PERSISTENCE ---
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
    st.info("Detecting fraud through behavioral patterns and card-specific limits.")
    col1, col2 = st.columns(2)
    if col1.button("Register", use_container_width=True):
        st.session_state['page'] = 'Register'; st.rerun()
    if col2.button("Login", use_container_width=True):
        st.session_state['page'] = 'Login'; st.rerun()

def register_page():
    st.title("📝 Register")
    fn = st.text_input("Full Name")
    un = st.text_input("Username")
    ph = st.text_input("Phone")
    pw = st.text_input("Password", type="password")
    if st.button("Register"):
        if un in st.session_state['users']: st.error("User exists!")
        elif validate_password(pw):
            st.session_state['users'][un] = {"password": pw, "name": fn, "phone": ph, "cards": [], "history": []}
            save_users(st.session_state['users'])
            st.success("Registered!"); st.session_state['page'] = 'Login'; st.rerun()
        else: st.error("Password too weak!")

def login_page():
    st.title("🔓 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in st.session_state['users'] and st.session_state['users'][u]['password'] == p:
            st.session_state['logged_in'], st.session_state['current_user'] = True, u
            st.session_state['page'] = 'Dashboard'; st.rerun()
    if st.button("Forgot Password?"):
        st.session_state['page'] = 'Forgot'; st.rerun()

def forgot_password_page():
    st.title("🔑 Reset")
    u = st.text_input("Username")
    ph = st.text_input("Phone")
    npw = st.text_input("New PW", type="password")
    if st.button("Update"):
        if u in st.session_state['users'] and st.session_state['users'][u]['phone'] == ph:
            st.session_state['users'][u]['password'] = npw
            save_users(st.session_state['users'])
            st.success("Updated!"); st.session_state['page'] = 'Login'; st.rerun()

def dashboard():
    user = st.session_state['current_user']
    user_data = st.session_state['users'][user]
    st.title(f"Welcome, {user_data['name']}")
    
    tab1, tab2, tab3 = st.tabs(["💳 Card Management", "🛡️ Fraud Analysis", "📜 History"])
    
    with tab1:
        st.subheader("Link a New Card")
        c_type = st.selectbox("Account Type", ["Savings", "Current"])
        c_num = st.text_input("Last 4 Digits", max_chars=4)
        c_limit = st.number_input("Set Max Withdrawal Limit per Transaction ($)", min_value=10, value=500)
        
        if st.button("Save Card"):
            user_data['cards'].append({"type": c_type, "num": c_num, "limit": c_limit})
            save_users(st.session_state['users'])
            st.success(f"Card Linked! Transaction Limit set to ${c_limit}")
        
        for c in user_data['cards']:
            st.write(f"✅ {c['type']} (xxxx-{c['num']}) | **Per-Withdrawal Limit: ${c['limit']}**")

    with tab2:
        st.header("Withdrawal Simulator")
        if not user_data['cards']:
            st.warning("Please add a card first.")
        else:
            options = [f"{c['type']} (xxxx-{c['num']})" for c in user_data['cards']]
            sel = st.selectbox("Select Card", options=options)
            card = next(i for i in user_data['cards'] if f"{i['type']} (xxxx-{i['num']})" == sel)
            
            amt = st.number_input("Withdrawal Amount ($)", value=50)
            dist = st.number_input("Distance from Home (km)", value=5)
            hr = st.slider("Hour", 0, 23, 12)
            
            if st.button("Verify Transaction"):
                status = ""
                # 1. Hard Transaction Limit Check
                if amt > card['limit']:
                    status = f"FAILED: Exceeded ${card['limit']} limit"
                    st.error(f"❌ {status}")
                else:
                    # 2. AI Pattern Check
                    model = IsolationForest(contamination=0.05).fit(get_training_data())
                    pred = model.predict(pd.DataFrame([[amt, hr, dist]], columns=['amount', 'hour', 'dist']))
                    if pred[0] == -1:
                        status = "FLAGGED: Unusual Behavior"
                        st.warning(f"⚠️ {status}")
                    else:
                        status = "APPROVED"
                        st.success(f"✅ {status}")
                
                # Log transaction
                user_data['history'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "card": sel, "amount": amt, "status": status
                })
                save_users(st.session_state['users'])

    with tab3:
        st.header("Recent Activity")
        if user_data['history']:
            st.table(pd.DataFrame(user_data['history']).iloc[::-1]) # Show latest first
        else:
            st.write("No transactions yet.")

# --- 5. NAVIGATION ---
if st.sidebar.button("Log Out"):
    st.session_state['logged_in'] = False
    st.session_state['page'] = 'Home'; st.rerun()

if st.session_state['page'] == 'Home': home_page()
elif st.session_state['page'] == 'Register': register_page()
elif st.session_state['page'] == 'Login': login_page()
elif st.session_state['page'] == 'Forgot': forgot_password_page()
elif st.session_state['page'] == 'Dashboard': dashboard()
