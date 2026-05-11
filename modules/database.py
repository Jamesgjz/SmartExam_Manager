def get_engine():
    # 1. Intentar obtener de variables de entorno (Local/Docker)
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")

    # 2. Si falla lo anterior, buscar en st.secrets de forma flexible
    if not user:
        # Intentar buscar dentro del grupo [database]
        if "database" in st.secrets:
            db_cfg = st.secrets["database"]
            user = db_cfg.get("user") or db_cfg.get("DB_USER")
            password = db_cfg.get("password") or db_cfg.get("DB_PASS")
            host = db_cfg.get("host") or db_cfg.get("DB_HOST")
            port = db_cfg.get("port") or db_cfg.get("DB_PORT", "5432")
            name = db_cfg.get("database") or db_cfg.get("DB_NAME")
        # Si no están en un grupo, buscarlos en la raíz de los secrets
        else:
            user = st.secrets.get("DB_USER") or st.secrets.get("user")
            password = st.secrets.get("DB_PASS") or st.secrets.get("password")
            host = st.secrets.get("DB_HOST") or st.secrets.get("host")
            port = st.secrets.get("DB_PORT") or st.secrets.get("port", "5432")
            name = st.secrets.get("DB_NAME") or st.secrets.get("database")

    # Si después de todo algo falta, lanzamos un error claro en los logs
    if not all([user, password, host, name]):
        st.error("⚠️ Error de configuración: Faltan credenciales en los Secrets.")
        return None

    try:
        # Neon SIEMPRE requiere sslmode=require
        url = f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode=require"
        return create_engine(url)
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None