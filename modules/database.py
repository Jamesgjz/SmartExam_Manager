import streamlit as st
from sqlalchemy import create_engine
import os

def get_engine():
    try:
        user = st.secrets.get("DB_USER") or os.getenv("DB_USER")
        password = st.secrets.get("DB_PASS") or os.getenv("DB_PASS")
        host = st.secrets.get("DB_HOST") or os.getenv("DB_HOST")
        port = st.secrets.get("DB_PORT") or "5432"
        name = st.secrets.get("DB_NAME") or os.getenv("DB_NAME")
        
        url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        return create_engine(url)
    except Exception:
        return None