import streamlit as st
import pandas as pd
from modules.database import engine
from sqlalchemy import text
from datetime import datetime

def registro_resultados():
    st.title("📊 Gestión de Calificaciones y Reportes")
    
    tab_registro, tab_historico = st.tabs(["🎯 Registrar Nota", "📋 Historial y Gestión"])

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

    # --- PESTAÑA 1: REGISTRO DE NOTA ---
    with tab_registro:
        with st.container(border=True):
            st.subheader("Búsqueda del Estudiante")
            id_raw = st.text_input("ID Banner del Estudiante", key="rep_id_banner")
            id_estudiante = id_raw.replace('.0', '').strip() if id_raw else ""
            
            nombre_estudiante, materias_estudiante = "", []
            
            if id_estudiante:
                with engine.connect() as conn:
                    res_est = conn.execute(text("SELECT nombre_completo FROM estudiantes WHERE CAST(id_estudiante AS TEXT) = :id"), {"id": id_estudiante}).fetchone()
                    if res_est:
                        nombre_estudiante = res_est[0]
                        st.success(f"✅ Estudiante: {nombre_estudiante}")
                        materias_estudiante = obtener_materias_estudiante(id_estudiante)
                    else:
                        st.error("Estudiante no encontrado.")

        if nombre_estudiante:
            st.subheader("Calificación de la Evaluación")
            
            col_asist, col_info = st.columns([1, 2])
            asistencia = col_asist.selectbox("¿Asistió el estudiante?", options=["Sí", "No"], key="asist_main")
            
            fecha_hoy_pc = datetime.now().strftime("%d/%m/%Y")
            col_info.info(f"📅 Fecha de registro: {fecha_hoy_pc}")

            with st.form("form_final_notas"):
                c1, c2 = st.columns(2)
                with c1:
                    materia_sel = st.selectbox("Materia a calificar", options=materias_estudiante)
                with c2:
                    if asistencia == "No":
                        nota_input = st.number_input("Nota (Bloqueada por inasistencia)", value=0.0, disabled=True)
                    else:
                        nota_input = st.number_input("Nota (0.0 - 5.0)", min_value=0.0, max_value=5.0, step=0.1, value=0.0)
                
                observaciones = st.text_area("Observaciones del docente")

                if st.form_submit_button("💾 Guardar Calificación Total", use_container_width=True):
                    try:
                        # 1. PASO DE PREPARACIÓN: Asegurar tabla y columna (Independiente)
                        with engine.begin() as conn:
                            conn.execute(text("""
                                CREATE TABLE IF NOT EXISTS notas_evaluaciones (
                                    id SERIAL PRIMARY KEY,
                                    id_estudiante TEXT,
                                    nombre_estudiante TEXT,
                                    materia TEXT,
                                    asistencia TEXT DEFAULT 'Sí',
                                    nota FLOAT,
                                    observaciones TEXT,
                                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """))
                        
                        # 2. INTENTO DE ALTERACIÓN (Separado para evitar bloqueos)
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("ALTER TABLE notas_evaluaciones ADD COLUMN asistencia TEXT DEFAULT 'Sí'"))
                        except:
                            pass # Ya existe la columna

                        # 3. PASO DE INSERCIÓN: Limpio y directo
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO notas_evaluaciones (id_estudiante, nombre_estudiante, materia, asistencia, nota, observaciones)
                                VALUES (:id_e, :nom_e, :mat, :asist, :nota, :obs)
                            """), {
                                "id_e": id_estudiante, "nom_e": nombre_estudiante, 
                                "mat": materia_sel, "asist": asistencia, "nota": nota_input, "obs": observaciones
                            })
                        
                        st.success(f"✅ ¡Guardado! Estudiante: {nombre_estudiante} - Nota: {nota_input}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    # --- PESTAÑA 2: HISTORIAL ---
    # --- PESTAÑA 2: HISTORIAL, EDICIÓN Y ELIMINACIÓN ---
    with tab_historico:
        st.subheader("Histórico de Notas Registradas")
        
        if st.button("🔄 Actualizar Tabla"):
            st.rerun()
            
        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT id, id_estudiante, nombre_estudiante, materia, asistencia, nota, 
                    CAST(fecha_registro AS DATE) as fecha_registro, observaciones
                    FROM notas_evaluaciones 
                    ORDER BY id DESC
                """)
                df_notas = pd.read_sql(query, conn)

            if not df_notas.empty:
                df_notas['Estado'] = df_notas['nota'].apply(lambda x: 'Aprobó' if x >= 3.5 else 'Reprobó')
                
                def color_estado(val):
                    if val == 'Aprobó':
                        return 'background-color: #d4edda; color: #155724; font-weight: bold'
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold'

                st.write(f"📋 **Total de registros encontrados: {len(df_notas)}**")
                st.dataframe(
                    df_notas.drop(columns=['id', 'id_estudiante']).style.map(color_estado, subset=['Estado']),
                    use_container_width=True, 
                    hide_index=True
                )
                
                st.divider()
                st.subheader("🛠️ Gestión de Calificaciones")
                
                opciones_n = {f"{r['nombre_estudiante']} | {r['materia']} (Nota: {r['nota']})": r['id'] for _, r in df_notas.iterrows()}
                seleccion_n = st.selectbox("Seleccione un registro para gestionar:", options=list(opciones_n.keys()), key="sel_gestion_notas")
                id_nota_sel = opciones_n[seleccion_n]

                col_ed, col_el = st.columns(2)

                if col_el.button("🗑️ Eliminar Nota", use_container_width=True):
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM notas_evaluaciones WHERE id = :id"), {"id": id_nota_sel})
                    st.success("Registro eliminado correctamente.")
                    st.rerun()

                if col_ed.button("✏️ Editar Nota", use_container_width=True, type="primary"):
                    st.session_state[f"edit_nota_{id_nota_sel}"] = True

                if st.session_state.get(f"edit_nota_{id_nota_sel}"):
                    reg_n = df_notas[df_notas['id'] == id_nota_sel].iloc[0]
                    materias_validas = obtener_materias_estudiante(reg_n['id_estudiante'])

                    with st.expander("📝 Formulario de Edición", expanded=True):
                        # --- MODIFICACIÓN MÍNIMA: Asistencia fuera del form para habilitar/deshabilitar nota ---
                        nueva_asist = st.selectbox("¿Asistió?", options=["Sí", "No"], 
                                                 index=0 if reg_n['asistencia'] == "Sí" else 1, key=f"asist_ed_{id_nota_sel}")

                        with st.form(f"form_edit_notas_{id_nota_sel}"):
                            st.write(f"Editando calificación de: **{reg_n['nombre_estudiante']}**")
                            ce1, ce2 = st.columns([2, 1])
                            
                            with ce1:
                                nueva_mat = st.selectbox("Materia", options=materias_validas, 
                                                       index=materias_validas.index(reg_n['materia']) if reg_n['materia'] in materias_validas else 0)
                            with ce2:
                                # Aquí la lógica de bloqueo reacciona a 'nueva_asist'
                                if nueva_asist == "No":
                                    nueva_nota = st.number_input("Nota", value=0.0, disabled=True)
                                else:
                                    # Si cambia a 'Sí', le permite editar. Si ya tenía nota, la pone; si no, 0.0
                                    val_defecto = float(reg_n['nota']) if reg_n['asistencia'] == "Sí" else 0.0
                                    nueva_nota = st.number_input("Nueva Nota", min_value=0.0, max_value=5.0, value=val_defecto, step=0.1)
                            
                            nuevas_obs = st.text_area("Observaciones", value=reg_n['observaciones'])

                            if st.form_submit_button("💾 Guardar Cambios"):
                                with engine.begin() as conn:
                                    conn.execute(text("""
                                        UPDATE notas_evaluaciones 
                                        SET materia = :m, asistencia = :a, nota = :n, observaciones = :o 
                                        WHERE id = :id
                                    """), {"m": nueva_mat, "a": nueva_asist, "n": nueva_nota, "o": nuevas_obs, "id": id_nota_sel})
                                st.success("Nota actualizada.")
                                del st.session_state[f"edit_nota_{id_nota_sel}"]
                                st.rerun()

                st.divider()
                st.download_button("📥 Descargar Reporte Completo (CSV)", df_notas.to_csv(index=False), "reporte_notas_final.csv")
            else:
                st.info("Aún no hay notas registradas.")
                
        except Exception as e:
            st.warning(f"Aviso: La tabla se está sincronizando... (Detalle: {e})")