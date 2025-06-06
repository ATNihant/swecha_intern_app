import streamlit as st
import pandas as pd
import os

USER_CSV = "data/users.csv"
UPLOAD_FOLDER = "uploads/offer_letters"

st.set_page_config(page_title="Register | Swecha Intern App")
st.title("📝 Intern Registration")

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load existing users
if os.path.exists(USER_CSV):
    users_df = pd.read_csv(USER_CSV)
else:
    users_df = pd.DataFrame(columns=["email", "password", "role", "name", "college", "offer_letter"])

with st.form("registration_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Create Password", type="password")
    college = st.text_input("College Name")
    role = st.selectbox("Role", ["AI Developer", "Tech Lead"])
    offer_letter = st.file_uploader("Upload Offer Letter (PDF)", type=["pdf"])

    submit = st.form_submit_button("Register")

    if submit:
        if not name or not email or not password or not college:
            st.warning("⚠️ Please fill out all fields.")
        elif email in users_df["email"].values:
            st.warning("⚠️ This email is already registered. Try logging in.")
        elif not offer_letter:
            st.warning("📄 Please upload your offer letter to proceed.")
        else:
            # Save uploaded offer letter
            safe_email = email.replace("@", "_at_").replace(".", "_dot_")
            offer_path = os.path.join(UPLOAD_FOLDER, f"{safe_email}.pdf")
            with open(offer_path, "wb") as f:
                f.write(offer_letter.getbuffer())

            # Create new user entry
            new_user = pd.DataFrame([{
                "email": email,
                "password": password,
                "role": role,
                "name": name,
                "college": college,
                "offer_letter": offer_path
            }])

            # Save to CSV
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            users_df.to_csv(USER_CSV, index=False)

            st.success("✅ Registration successful! You can now log in.")
            st.balloons()
