import streamlit as st
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    
    if not user:
        try:
            user = st.secrets["DB_USER"]
            password = st.secrets["DB_PASS"]
            host = st.secrets["DB_HOST"]
            port = st.secrets["DB_PORT"]
            name = st.secrets["DB_NAME"]
        except: return None

    try:
        url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        return create_engine(url)
    except: return None

engine = get_engine()