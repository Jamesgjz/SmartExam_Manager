import streamlit as st
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

def get_engine():
    # 1. Intentar obtener de variables de entorno (Local)
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")

    # 2. Si no hay variables locales, buscar en st.secrets
    if not user:
        if "database" in st.secrets:
            db_cfg = st.secrets["database"]
            user = db_cfg.get("user")
            password = db_cfg.get("password")
            host = db_cfg.get("host")
            port = db_cfg.get("port", "5432")
            name = db_cfg.get("database")
        else:
            # Si ni siquiera encuentra el grupo [database]
            st.error("❌ No se encontró el grupo [database] en los Secrets.")
            return None

    # Verificación de seguridad (esto saldrá en tu app si falta algo)
    if not all([user, password, host, name]):
        st.warning(f"⚠️ Faltan datos: user={bool(user)}, pass={bool(password)}, host={bool(host)}, db={bool(name)}")
        return None

    try:
        url = f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode=require"
        return create_engine(url)
    except Exception as e:
        st.error(f"❌ Error de SQLAlchemy: {e}")
        return None

engine = get_engine()