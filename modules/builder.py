import streamlit as st
import pandas as pd
from modules.database import engine
from sqlalchemy import text
from datetime import datetime

def estado_construccion_malla():
    st.title("🏗️ Constructor de Malla Curricular")
    
    tab_malla, tab_gestion = st.tabs(["📊 Vista de Malla (Semáforo)", "⚙️ Gestión de Avance"])

    # --- FUNCIÓN PARA OBTENER ASIGNATURAS REALES ---
    def obtener_asignaturas_registradas():
        try:
            with engine.connect() as conn:
                # Consultamos tu tabla maestra de asignaturas
                query = text("SELECT codigo_alfa, nombre_asignatura FROM asignaturas ORDER BY nombre_asignatura")
                res = conn.execute(query).fetchall()
                return {f"{r[0]} - {r[1]}": r[0] for r in res}
        except Exception as e:
            st.error(f"Error al conectar con la base de materias: {e}")
            return {}

    # --- PESTAÑA 1: VISTA DE SEMÁFORO ---
    with tab_malla:
        st.subheader("Estado General del Microcurrículo")
        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT m.codigo_alfa, m.nombre_materia, m.estado, m.semestre, m.observaciones
                    FROM malla_curricular m
                    ORDER BY m.semestre ASC, m.nombre_materia ASC
                """)
                df_malla = pd.read_sql(query, conn)

            if not df_malla.empty:
                # Métricas
                c1, c2, c3 = st.columns(3)
                c1.metric("✅ Construidas", len(df_malla[df_malla['estado'] == 'Construida']))
                c2.metric("🚧 En Proceso", len(df_malla[df_malla['estado'] == 'En construcción']))
                c3.metric("🔴 Pendientes", len(df_malla[df_malla['estado'] == 'Pendiente por hacer']))

                def aplicar_semaforo(val):
                    if val == 'Construida':
                        return 'background-color: #d4edda; color: #155724; font-weight: bold'
                    elif val == 'En construcción':
                        return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                    else:
                        return 'background-color: #f8d7da; color: #721c24; font-weight: bold'

                st.dataframe(
                    df_malla.style.map(aplicar_semaforo, subset=['estado']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No hay materias reportadas en la malla aún.")
        except:
            st.info("La malla se visualizará cuando asigne el primer estado de construcción.")

    # --- PESTAÑA 2: GESTIÓN (SIN ENTRADA MANUAL) ---
    with tab_gestion:
        st.subheader("Asignar Estado de Construcción")
        
        # 1. Obtener el diccionario de materias reales { "ID - Nombre": "ID" }
        materias_dict = obtener_asignaturas_registradas()
        
        if materias_dict:
            with st.form("form_builder_integridad"):
                st.write("Seleccione una asignatura existente para actualizar su estado:")
                
                # Desplegable con materias reales
                seleccion_materia = st.selectbox("Seleccionar Asignatura", options=list(materias_dict.keys()))
                codigo_alfa_sel = materias_dict[seleccion_materia]
                nombre_materia_sel = seleccion_materia.split(" - ")[1]
                
                c1, c2 = st.columns(2)
                with c1:
                    estado_m = st.selectbox(
                        "Estado de Avance", 
                        options=["Pendiente por hacer", "En construcción", "Construida"]
                    )
                with c2:
                    semestre_m = st.number_input("Semestre en la Malla", min_value=1, max_value=10, value=1)
                
                obs_m = st.text_area("Observaciones técnicas de la construcción")

                if st.form_submit_button("💾 Actualizar Estado en Malla", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            # Asegurar tabla de malla
                            conn.execute(text("""
                                CREATE TABLE IF NOT EXISTS malla_curricular (
                                    id SERIAL PRIMARY KEY,
                                    codigo_alfa TEXT UNIQUE,
                                    nombre_materia TEXT,
                                    estado TEXT,
                                    semestre INTEGER,
                                    observaciones TEXT,
                                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """))
                            
                            # Upsert por codigo_alfa
                            conn.execute(text("""
                                INSERT INTO malla_curricular (codigo_alfa, nombre_materia, estado, semestre, observaciones)
                                VALUES (:cod, :nom, :est, :sem, :obs)
                                ON CONFLICT (codigo_alfa) DO UPDATE SET
                                    estado = EXCLUDED.estado,
                                    semestre = EXCLUDED.semestre,
                                    observaciones = EXCLUDED.observaciones,
                                    fecha_actualizacion = CURRENT_TIMESTAMP
                            """), {
                                "cod": codigo_alfa_sel, 
                                "nom": nombre_materia_sel, 
                                "est": estado_m, 
                                "sem": semestre_m, 
                                "obs": obs_m
                            })
                        st.success(f"Estado actualizado para: {nombre_materia_sel}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No se encontraron asignaturas registradas. Primero debe cargar las asignaturas en el módulo correspondiente.")

        # Opción de limpieza
        st.divider()
        st.subheader("🗑️ Quitar de la Malla")
        try:
            with engine.connect() as conn:
                df_del = pd.read_sql(text("SELECT codigo_alfa, nombre_materia FROM malla_curricular"), conn)
            if not df_del.empty:
                op_del = {f"{r[0]} - {r[1]}": r[0] for _, r in df_del.iterrows()}
                sel_del = st.selectbox("Materia a quitar del reporte:", options=list(op_del.keys()))
                if st.button("❌ Eliminar de la Vista"):
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM malla_curricular WHERE codigo_alfa = :cod"), {"cod": op_del[sel_del]})
                    st.rerun()
        except:
            pass