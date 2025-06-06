import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

from dashboards.admin_dashboard import show_admin_dashboard
from dashboards.tech_lead_dashboard import show_tech_lead_dashboard
from dashboards.ai_developer_dashboard import show_ai_developer_dashboard

USERS_CSV = "data/users.csv"

# Initialize users.csv if not exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(USERS_CSV):
    pd.DataFrame(columns=["name", "email", "password", "role", "college"]).to_csv(USERS_CSV, index=False)

def register_user():
    st.subheader("👤 Register")

    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["AI Developer", "Tech Lead", "Admin"])
        college = st.text_input("College Name")
        offer_letter = st.file_uploader("Upload Offer Letter (PDF)", type=["pdf"])

        submit = st.form_submit_button("Register")

        if submit:
            if not name or not email or not password or not college or offer_letter is None:
                st.error("❌ Please fill in all fields and upload your offer letter.")
                return

            users_df = pd.read_csv(USERS_CSV)
            if email in users_df["email"].values:
                st.error("❌ Email already registered.")
                return

            new_user = pd.DataFrame([{
                "name": name,
                "email": email,
                "password": password,
                "role": role,
                "college": college
            }])
            users_df = pd.concat([users_df, new_user], ignore_index=True)

            users_df.to_csv(USERS_CSV, index=False)
            st.success("✅ Registration successful! Please login.")
            st.session_state.page = "login"

def login_user():
    st.subheader("🔐 Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            users_df = pd.read_csv(USERS_CSV)
            user = users_df[(users_df["email"] == email) & (users_df["password"] == password)]

            if not user.empty:
                user_info = user.iloc[0]
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.role = user_info["role"]
                st.session_state.name = user_info["name"]
                st.session_state.college = user_info["college"]
                st.session_state.login_time = datetime.now().isoformat()

                st.success(f"✅ Welcome back, {user_info['name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

def logout_user():
    for key in ["logged_in", "email", "role", "college", "page", "login_time"]:
        st.session_state.pop(key, None)
    st.success("🔒 Logged out successfully.")

def main():
    st.set_page_config(page_title="Swecha Intern Portal", layout="wide")

    # Default session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.page = "login"

    # Check for session timeout (30 minutes)
    if st.session_state.get("logged_in"):
        try:
            login_time = datetime.fromisoformat(st.session_state.get("login_time", datetime.min.isoformat()))
            if datetime.now() - login_time > timedelta(minutes=30):
                st.warning("⏱️ Session timed out. Please log in again.")
                logout_user()
                st.rerun()
        except Exception:
            logout_user()
            st.rerun()

    # Logged-in flow
    if st.session_state.logged_in:
        st.sidebar.markdown(f"👤 **Logged in as:** {st.session_state.email}")
        st.sidebar.markdown(f"🎓 **Role:** {st.session_state.role}")
        st.sidebar.markdown(f"🏫 **College:** {st.session_state.college}")
        if st.sidebar.button("🚪 Logout"):
            logout_user()
            st.rerun()

        # Show respective dashboards
        if st.session_state.role == "Admin":
            show_admin_dashboard()
        elif st.session_state.role == "Tech Lead":
            show_tech_lead_dashboard(st.session_state.college)
        elif st.session_state.role == "AI Developer":
            show_ai_developer_dashboard(st.session_state.email)

    # Not logged in
    else:
        st.title("🧠 Swecha Intern Management Portal")
        choice = st.sidebar.radio("Choose", ["Login", "Register"])

        if choice == "Login":
            st.session_state.page = "login"
            login_user()
        else:
            st.session_state.page = "register"
            register_user()

if __name__ == "__main__":
    main()
