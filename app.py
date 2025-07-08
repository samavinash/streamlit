import streamlit as st
import streamlit_authenticator as stauth

# Dummy user data
names = ['admin']
usernames = ['admin']
passwords = ['123']

hashed_pw = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_pw,
    'cookie_name', 'signature_key', cookie_expiry_days=1
)

name, auth_status, username = authenticator.login('Login', 'main')

if auth_status:
    st.success(f"Welcome {name}")
    st.title("Production-Ready Streamlit App with Auth")
    st.write("Secure, containerized, and proxied with Nginx.")
elif auth_status is False:
    st.error("Invalid username or password")
else:
    st.warning("Please enter your credentials")
