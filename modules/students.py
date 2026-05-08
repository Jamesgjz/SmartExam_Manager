import streamlit as st
import pandas as pd
from modules.database import get_engine

engine = get_engine()

def registrar_nueva_solicitud():
    st.subheader("🆕 Registro de Solicitud Individual")
    with st.form("form_estudiante"):
        c1, c2 = st.columns(2)
        with c1:
            id_est = st.text_input("ID Banner")
            nombre = st.text_input("Nombre Completo")
            correo = st.text_input("Correo Institucional")
        with c2:
            programa = st.selectbox("Programa", ["Ing. Software", "Sistemas", "Tecnología"])
            estado_mat = st.selectbox("Estado Matrícula", ["Matriculado", "No matriculado", "Admitido"])
            
        submit = st.form_submit_button("Insertar Estudiante")
        
        if submit and id_est and nombre:
            query = f"""
                INSERT INTO estudiantes (id_estudiante, nombre_completo, correo, programa, estado_matricula)
                VALUES ('{id_est}', '{nombre}', '{correo}', '{programa}', '{estado_mat}')
                ON CONFLICT (id_estudiante) DO UPDATE SET estado_matricula = EXCLUDED.estado_matricula;
            """
            with engine.connect() as conn:
                conn.execute(query)
            st.success(f"Estudiante {nombre} registrado/actualizado.")