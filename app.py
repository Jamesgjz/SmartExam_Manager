import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. CARGA DE CONFIGURACIÓN
if os.path.exists(".env"):
    load_dotenv()

# Conexión a la DB (usa variables de entorno locales o secretos de Streamlit)
def get_engine():
    user = st.secrets["DB_USER"] if "DB_USER" in st.secrets else os.getenv("DB_USER")
    password = st.secrets["DB_PASS"] if "DB_PASS" in st.secrets else os.getenv("DB_PASS")
    host = st.secrets["DB_HOST"] if "DB_HOST" in st.secrets else os.getenv("DB_HOST")
    port = st.secrets["DB_PORT"] if "DB_PORT" in st.secrets else os.getenv("DB_PORT")
    name = st.secrets["DB_NAME"] if "DB_NAME" in st.secrets else os.getenv("DB_NAME")
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)

engine = get_engine()

# Configuración de la interfaz
st.set_page_config(page_title="SmartExam Manager", layout="wide", page_icon="🛡️")

# --- FUNCIONES DE MÓDULOS ---

def mostrar_inicio():
    st.title("🛡️ SmartExam Manager - Panel de Control")
    
    # KPIs Relevantes
    st.subheader("Información de Interés Hoy")
    col1, col2, col3 = st.columns(3)
    
    try:
        total_est = pd.read_sql("SELECT count(*) FROM estudiantes", engine).iloc[0,0]
        col1.metric("Estudiantes en Base de Datos", total_est)
    except:
        col1.metric("Estudiantes", "Error DB")
        
    col2.metric("Pendientes por Evaluar", "12") # Esto será dinámico pronto
    col3.metric("Eficiencia de Gestión", "92%")

    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("**Recordatorio:** Mañana se cierran las actas del Momento 1.")
    with c2:
        st.success("**Novedad:** La sincronización con el Excel fue exitosa.")

def mostrar_registro_solicitud():
    st.subheader("🆕 Registrar Nueva Solicitud")
    st.write("Usa este formulario para añadir estudiantes que llegan por fuera del Excel masivo.")
    
    with st.form("form_registro"):
        c1, c2 = st.columns(2)
        with c1:
            id_est = st.text_input("ID del Estudiante (Banner)")
            nombre = st.text_input("Nombre Completo")
            correo = st.text_input("Correo Institucional")
        with c2:
            programa = st.text_input("Programa Académico")
            observacion = st.text_area("Observaciones adicionales")
            
        boton_guardar = st.form_submit_button("Guardar en Base de Datos")
        
        if boton_guardar:
            if id_est and nombre:
                # COMANDO SQL PARA INSERTAR REALMENTE
                query = f"""
                    INSERT INTO estudiantes (id_estudiante, nombre_completo, correo, programa, estado_matricula)
                    VALUES ('{id_est}', '{nombre}', '{correo}', '{programa}', '{observacion}')
                    ON CONFLICT (id_estudiante) DO NOTHING;
                """
                with engine.connect() as conn:
                    conn.execute(query)
                st.success(f"✅ ¡{nombre} ha sido registrado exitosamente!")
            else:
                st.error("Por favor completa al menos el ID y el Nombre.")

def mostrar_gestion_estudiantes():
    st.subheader("📊 Listado Maestro")
    df = pd.read_sql("SELECT * FROM estudiantes", engine)
    st.dataframe(df, use_container_width=True)

# --- LÓGICA PRINCIPAL ---

def main():
    st.sidebar.title("Menú Principal")
    modulo = st.sidebar.radio(
        "Seleccione una tarea:",
        ["🏠 Inicio", "🆕 Nueva Solicitud", "📊 Ver Estudiantes"]
    )

    if modulo == "🏠 Inicio":
        mostrar_inicio()
    elif modulo == "🆕 Nueva Solicitud":
        mostrar_registro_solicitud()
    elif modulo == "📊 Ver Estudiantes":
        mostrar_gestion_estudiantes()

if __name__ == "__main__":
    main()