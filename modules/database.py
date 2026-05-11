import streamlit as st
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

def get_engine():
    # 1. Intentar obtener de variables de entorno (Docker/Local)
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")

    # 2. Si no hay variables de entorno, buscar en st.secrets (Streamlit Cloud)
    if not user and "database" in st.secrets:
        db_cfg = st.secrets["database"]
        user = db_cfg.get("user")
        password = db_cfg.get("password")
        host = db_cfg.get("host")
        port = db_cfg.get("port", "5432")
        name = db_cfg.get("database")

    if not all([user, password, host, name]):
        return None

    try:
        # Nota: Neon requiere sslmode=require para conexiones externas
        url = f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode=require"
        return create_engine(url)
    except Exception as e:
        print(f"Error creando el engine: {e}")
        return None

engine = get_engine()