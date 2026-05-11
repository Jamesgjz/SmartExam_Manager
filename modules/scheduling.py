import streamlit as st
import pandas as pd
from modules.database import engine
from sqlalchemy import text
from datetime import datetime

def programar_evaluaciones():
    st.title("📅 Programación de Evaluaciones")
    
    tab_registro, tab_listado = st.tabs(["📝 Agendar Evaluación", "📋 Evaluaciones Agendadas"])

    # --- FUNCIONES DE APOYO ---
    def obtener_profesores():
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT nombre_docente FROM docentes ORDER BY nombre_docente")).fetchall()
                return [p[0] for p in res]
        except: return []

    def obtener_materias_estudiante(id_est):
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT DISTINCT COALESCE(a.nombre_asignatura, s.materia_pendiente) 
                    FROM seguimiento s 
                    LEFT JOIN asignaturas a ON s.codigo_alfa = a.codigo_alfa 
                    WHERE CAST(s.id_estudiante AS TEXT) = :id
                """), {"id": id_est}).fetchall()
                return [m[0] for m in res]
        except: return []

    # --- PESTAÑA 1: REGISTRO ---
    with tab_registro:
        with st.expander("👨‍🏫 Gestión de Profesores"):
            col_p1, col_p2 = st.columns([2, 1])
            nuevo_profesor = col_p1.text_input("Nombre del nuevo Profesor")
            if col_p2.button("➕ Registrar", use_container_width=True):
                if nuevo_profesor:
                    with engine.connect() as conn:
                        conn.execute(text("CREATE TABLE IF NOT EXISTS docentes (nombre_docente TEXT PRIMARY KEY)"))
                        conn.execute(text("INSERT INTO docentes (nombre_docente) VALUES (:nom) ON CONFLICT DO NOTHING"), {"nom": nuevo_profesor.strip()})
                        conn.commit()
                    st.rerun()

        with st.container(border=True):
            id_raw = st.text_input("ID Banner del Estudiante", key="reg_id_banner")
            id_estudiante = id_raw.replace('.0', '').strip() if id_raw else ""
            nombre_estudiante, materias_estudiante = "", []
            
            if id_estudiante:
                with engine.connect() as conn:
                    res_est = conn.execute(text("SELECT nombre_completo FROM estudiantes WHERE CAST(id_estudiante AS TEXT) = :id"), {"id": id_estudiante}).fetchone()
                    if res_est:
                        nombre_estudiante = res_est[0]
                        st.success(f"✅ {nombre_estudiante}")
                        materias_estudiante = obtener_materias_estudiante(id_estudiante)
                    else:
                        st.error("Estudiante no encontrado.")

        if nombre_estudiante:
            with st.form("form_agendar"):
                st.subheader("Detalles de la Evaluación")
                c1, c2 = st.columns(2)
                with c1:
                    materia_sel = st.selectbox("Materia", options=materias_estudiante)
                    fecha_eval = st.date_input("Fecha Evaluación", min_value=datetime.today())
                with c2:
                    profs = obtener_profesores()
                    profesor_sel = st.selectbox("Profesor", options=profs if profs else ["Debe registrar profesores"])
                    hora_eval = st.time_input("Hora")
                
                modalidad = st.radio("Modalidad", ["Teams (Virtual)", "Presencial"], horizontal=True)
                
                if st.form_submit_button("💾 Agendar", use_container_width=True):
                    if profs:
                        with engine.connect() as conn:
                            conn.execute(text("""
                                CREATE TABLE IF NOT EXISTS agenda_evaluaciones (
                                    id SERIAL PRIMARY KEY, id_estudiante TEXT, nombre_estudiante TEXT, 
                                    materia TEXT, fecha DATE, hora TIME, profesor TEXT, modalidad TEXT, 
                                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """))
                            conn.execute(text("""
                                INSERT INTO agenda_evaluaciones (id_estudiante, nombre_estudiante, materia, fecha, hora, profesor, modalidad)
                                VALUES (:id_e, :nom_e, :mat, :fec, :hor, :prof, :mod)
                            """), {"id_e": id_estudiante, "nom_e": nombre_estudiante, "mat": materia_sel, "fec": fecha_eval, "hor": hora_eval, "prof": profesor_sel, "mod": modalidad})
                            conn.commit()
                        st.success("Agendado correctamente.")
                        st.rerun()

    # --- PESTAÑA 2: LISTADO Y EDICIÓN ---
    with tab_listado:
        st.subheader("Evaluaciones Programadas")
        try:
            with engine.connect() as conn:
                # CAST a DATE para programado_el limpia el formato YYYY-MM-DD
                query = text("""
                    SELECT id, id_estudiante, nombre_estudiante, materia, fecha, hora, profesor, modalidad, 
                    CAST(fecha_registro AS DATE) as programado_el 
                    FROM agenda_evaluaciones ORDER BY fecha_registro DESC
                """)
                df_agenda = pd.read_sql(query, conn)

            if not df_agenda.empty:
                st.dataframe(df_agenda.drop(columns=['id', 'id_estudiante']), use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("🛠️ Modificar o Eliminar")
                opciones = {f"{r['nombre_estudiante']} - {r['materia']} ({r['fecha']})": r['id'] for _, r in df_agenda.iterrows()}
                id_seleccionado = st.selectbox("Seleccione un registro para gestionar:", options=list(opciones.keys()))
                registro_id = opciones[id_seleccionado]
                
                col_btn1, col_btn2 = st.columns(2)
                
                if col_btn2.button("🗑️ Eliminar Registro", use_container_width=True, type="secondary"):
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM agenda_evaluaciones WHERE id = :id"), {"id": registro_id})
                        conn.commit()
                    st.rerun()

                if col_btn1.button("✏️ Editar Registro", use_container_width=True, type="primary"):
                    st.session_state[f"edit_mode_{registro_id}"] = True

                if st.session_state.get(f"edit_mode_{registro_id}"):
                    with st.expander("📝 Formulario de Edición Controlada", expanded=True):
                        reg_actual = df_agenda[df_agenda['id'] == registro_id].iloc[0]
                        # Recuperamos las materias válidas del estudiante para este ID
                        materias_validas = obtener_materias_estudiante(reg_actual['id_estudiante'])
                        
                        with st.form("form_editar"):
                            st.write(f"Editando: **{reg_actual['nombre_estudiante']}**")
                            c1, c2 = st.columns(2)
                            with c1:
                                nueva_mat = st.selectbox("Materia", options=materias_validas, 
                                                       index=materias_validas.index(reg_actual['materia']) if reg_actual['materia'] in materias_validas else 0)
                                nueva_fecha = st.date_input("Nueva Fecha", value=reg_actual['fecha'])
                            with c2:
                                profs = obtener_profesores()
                                nuevo_prof = st.selectbox("Cambiar Profesor", options=profs, 
                                                        index=profs.index(reg_actual['profesor']) if reg_actual['profesor'] in profs else 0)
                                nueva_hora = st.time_input("Nueva Hora", value=reg_actual['hora'])
                            
                            if st.form_submit_button("Guardar Cambios"):
                                with engine.connect() as conn:
                                    conn.execute(text("""
                                        UPDATE agenda_evaluaciones 
                                        SET materia=:m, fecha=:f, hora=:h, profesor=:p 
                                        WHERE id=:id
                                    """), {"m": nueva_mat, "f": nueva_fecha, "h": nueva_hora, "p": nuevo_prof, "id": registro_id})
                                    conn.commit()
                                st.success("Actualizado con éxito.")
                                del st.session_state[f"edit_mode_{registro_id}"]
                                st.rerun()
            else:
                st.info("No hay registros.")
        except Exception as e:
            st.info("Inicia el agendado para activar esta sección.")