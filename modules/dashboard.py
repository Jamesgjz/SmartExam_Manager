import streamlit as st

def mostrar_kpis_reales():
    st.header("📊 Dashboards de Gestión")
    col1, col2 = st.columns(2)
    col1.metric("Total Estudiantes", "150")
    col2.metric("Pruebas Pendientes", "23")