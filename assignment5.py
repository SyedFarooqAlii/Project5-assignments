import streamlit as st
import hashlib
from cryptography.fernet import Fernet

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0  
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}  
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text, passkey):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    if st.session_state.failed_attempts >= 3:
        st.warning("🔒 Too many failed attempts! Redirecting to Login Page.")
        st.experimental_rerun()

    hashed_passkey = hash_passkey(passkey)

    for key, value in st.session_state.stored_data.items():
        if value["encrypted_text"] == encrypted_text and value["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0  # Reset failed attempts on success
            return cipher.decrypt(encrypted_text.encode()).decode()

    st.session_state.failed_attempts += 1  
    return None


st.title("🔒 Secure Data Encryption System")


menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")

elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")
    user_data = st.text_area("Enter Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data, passkey)
            st.session_state.stored_data[encrypted_text] = {"encrypted_text": encrypted_text, "passkey": hashed_passkey}
            st.success("✅ Data stored securely!")
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")
    encrypted_text = st.text_area("Enter Encrypted Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_text and passkey:
            decrypted_text = decrypt_data(encrypted_text, passkey)

            if decrypted_text:
                st.success(f"✅ Decrypted Data: {decrypted_text}")
            else:
                st.error(f"❌ Incorrect passkey! Attempts remaining: {3 - st.session_state.failed_attempts}")
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")
    login_pass = st.text_input("Enter Master Password:", type="password")

    if st.button("Login"):
        if login_pass == "admin123": 
            st.session_state.failed_attempts = 0  
            st.success("✅ Reauthorized successfully! Redirecting to Retrieve Data...")
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect password!")
