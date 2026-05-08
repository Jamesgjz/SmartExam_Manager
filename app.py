import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

# Configuración de la interfaz
st.set_page_config(page_title="SmartExam Manager", layout="wide")

def main():
    # --- MENÚ LATERAL (Selector de Módulos) ---
    st.sidebar.title("Navegación")
    st.sidebar.info("Seleccione la tarea que desea realizar hoy.")
    
    # Aquí definimos los módulos que vamos a ir construyendo
    modulo = st.sidebar.radio(
        "¿Qué desea hacer?",
        [
            "🏠 Inicio / Resumen",
            "📊 Gestión de Estudiantes",
            "📅 Programar Citaciones",
            "📧 Enviar Notificaciones",
            "✅ Calificador y Notas"
        ]
    )

    # --- LÓGICA DE MÓDULOS ---
    if modulo == "🏠 Inicio / Resumen":
        mostrar_inicio()
    
    elif modulo == "📊 Gestión de Estudiantes":
        mostrar_gestion_estudiantes()
        
    elif modulo == "📅 Programar Citaciones":
        st.subheader("Módulo en construcción...")
        st.write("Aquí vincularemos con Teams para generar enlaces.")

# --- DEFINICIÓN DE CADA MÓDULO (Funciones) ---

def mostrar_inicio():
    st.title("🛡️ SmartExam Manager - UNIMINUTO")
    st.markdown("Bienvenido al sistema de automatización para pruebas de suficiencia.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Este sistema permite gestionar los 150 estudiantes por curso de manera eficiente y humanizada.")
    with col2:
        st.warning("Recuerde que los cambios realizados aquí se sincronizan con su base de datos local.")

def mostrar_gestion_estudiantes():
    st.subheader("📊 Listado de Estudiantes y Malla")
    st.write("Este módulo permite visualizar la información migrada desde el Excel.")
    # Aquí iría el código para mostrar la tabla de PostgreSQL

if __name__ == "__main__":
    main()