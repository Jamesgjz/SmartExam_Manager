import streamlit as st
import pandas as pd
from modules.database import engine
from sqlalchemy import text
import unicodedata
import time

def registrar_nueva_solicitud():
    st.title("👥 Gestión de Estudiantes y Seguimiento")
    
    # Estructura de pestañas para manejo de flujo pesado
    tab_registro, tab_consulta = st.tabs([
        "🆕 Registro Individual de Casos", 
        "🔍 Consulta, Estado y Disponibilidad"
    ])

    # --- FUNCIÓN INTERNA DE NORMALIZACIÓN (Garantiza integridad de datos) ---
    def normalizar_texto(texto):
        if not texto: return ""
        texto = str(texto).strip().upper()
        # Normalización NFD para eliminar tildes y caracteres especiales
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                          if unicodedata.category(c) != 'Mn')
        return texto

    # --- PESTAÑA 1: REGISTRO INDIVIDUAL CON LIMPIEZA AUTOMÁTICA ---
    with tab_registro:
        st.subheader("Registro Manual de Casos Especiales")
        
        with st.container(border=True):
            col_id, col_nom = st.columns([1, 2])
            
            # Los widgets usan keys para que el st.rerun() los resetee al valor por defecto
            id_banner = col_id.text_input("ID Banner", key="reg_id_manual", help="Ingrese el código único del estudiante")
            nombre_raw = col_nom.text_input("Nombre Completo", key="reg_nom_manual")
            
            col_est, col_mat = st.columns(2)
            estado_mat = col_est.selectbox(
                "Estado de Matrícula", 
                ["Matriculado", "No matriculado", "Admitido", "No Admitido por documentos"],
                key="reg_est_manual"
            )
            
            # Consultamos las materias de la malla oficial
            try:
                query_asig = text("SELECT nombre_asignatura, codigo_alfa FROM asignaturas ORDER BY nombre_asignatura")
                with engine.connect() as conn:
                    df_asig = pd.read_sql(query_asig, conn)
                dict_materias = {f"{row['codigo_alfa']} - {row['nombre_asignatura']}": row['codigo_alfa'] for _, row in df_asig.iterrows()}
                materias_elegidas = col_mat.multiselect("Asignaturas a evaluar", list(dict_materias.keys()), key="reg_mat_manual")
            except Exception as e:
                st.warning(f"⚠️ Configure la Malla Curricular primero. (Error: {e})")
                materias_elegidas = []

            observaciones = st.text_area("Observaciones o notas de seguimiento", key="reg_obs_manual")

            if st.button("🚀 Registrar Solicitud Completa", use_container_width=True):
                if id_banner and nombre_raw:
                    nombre_clean = normalizar_texto(nombre_raw)
                    id_clean = id_banner.strip().replace('.0', '')
                    
                    with st.status("Sincronizando con base de datos...", expanded=False) as status:
                        try:
                            # 1. Asegurar estructura de seguimiento (Evita errores de transacción abortada)
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    CREATE TABLE IF NOT EXISTS seguimiento (
                                        id SERIAL PRIMARY KEY,
                                        id_estudiante TEXT,
                                        codigo_alfa TEXT,
                                        nota FLOAT DEFAULT 0.0,
                                        materia_pendiente TEXT,
                                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    )
                                """))
                                try:
                                    conn.execute(text("ALTER TABLE seguimiento ADD CONSTRAINT unique_est_mat UNIQUE (id_estudiante, codigo_alfa)"))
                                except:
                                    pass # Si ya existe el índice, continuamos

                            # 2. Transacción de Registro (Estudiante + Materias)
                            with engine.begin() as conn:
                                # Verificamos si es nuevo para personalizar el mensaje
                                check_est = conn.execute(text("SELECT 1 FROM estudiantes WHERE id_estudiante = :id"), {"id": id_clean}).fetchone()

                                # Upsert del Estudiante
                                conn.execute(text("""
                                    INSERT INTO estudiantes (id_estudiante, nombre_completo, estado_matricula) 
                                    VALUES (:id, :nom, :est) 
                                    ON CONFLICT (id_estudiante) DO UPDATE SET 
                                        nombre_completo = EXCLUDED.nombre_completo,
                                        estado_matricula = EXCLUDED.estado_matricula
                                """), {"id": id_clean, "nom": nombre_clean, "est": estado_mat})
                                
                                nuevos_cont = 0
                                for m in materias_elegidas:
                                    cod_alfa = dict_materias[m]
                                    # Verificar si la materia ya estaba para el conteo de feedback
                                    check_mat = conn.execute(text("SELECT 1 FROM seguimiento WHERE id_estudiante = :id AND codigo_alfa = :cod"), 
                                                            {"id": id_clean, "cod": cod_alfa}).fetchone()
                                    if not check_mat: nuevos_cont += 1

                                    conn.execute(text("""
                                        INSERT INTO seguimiento (id_estudiante, codigo_alfa, nota, materia_pendiente) 
                                        VALUES (:id, :cod, 0.0, :obs)
                                        ON CONFLICT (id_estudiante, codigo_alfa) DO UPDATE SET
                                            materia_pendiente = EXCLUDED.materia_pendiente
                                    """), {"id": id_clean, "cod": cod_alfa, "obs": observaciones})
                                
                                status.update(label="¡Registro completado!", state="complete")

                            # --- RETROALIMENTACIÓN VISUAL ---
                            if not check_est:
                                st.success(f"✅ ¡Nuevo Registro! {nombre_clean} ha sido creado.")
                                st.balloons()
                            elif nuevos_cont > 0:
                                st.success(f"✅ Se agregaron {nuevos_cont} materias nuevas al perfil de {nombre_clean}.")
                            else:
                                st.info(f"ℹ️ El registro de {nombre_clean} ya existía. Se actualizaron las observaciones.")

                            # --- LIMPIEZA AUTOMÁTICA DE CAMPOS ---
                            # Esperamos un momento para que el usuario lea el mensaje y reiniciamos
                            time.sleep(1.5)
                            st.rerun() # Al no haber valores manuales en el session_state, los widgets vuelven a vacío

                        except Exception as e:
                            status.update(label="Falla en base de datos", state="error")
                            st.error(f"Error técnico: {e}")
                else:
                    st.error("Los campos ID Banner y Nombre son obligatorios.")

    # --- PESTAÑA 2: CONSULTA, ESTADO Y DISPONIBILIDAD (SEMÁFORO) ---
    with tab_consulta:
        st.subheader("Listado Maestro: Seguimiento Sincronizado")
        c_busq, c_filt, c_disp = st.columns([2, 1, 1])
        busqueda = c_busq.text_input("🔍 Buscar por Nombre o ID", placeholder="Ej: Oscar Andrade...", key="query_search_key")
        estado_filtro = c_filt.selectbox("Filtrar Resultado", ["Todos", "✅ Aprobó", "❌ Reprobó", "⏳ Pendiente"], key="filter_res_key")
        disp_filtro = c_disp.selectbox("Estado en Malla", ["Todos", "Construida", "En construcción", "Pendiente"], key="filter_malla_key")
        
        try:
            # Query maestra que une Seguimiento con el Estado de Construcción de la Malla
            query_maestra = text("""
                SELECT e.id_estudiante AS "ID", e.nombre_completo AS "Estudiante",
                       COALESCE(a.nombre_asignatura, s.materia_pendiente, 'No asignada') AS "Asignatura",
                       COALESCE(m.estado, 'Pendiente') AS "Estado_Malla",
                       CASE WHEN s.nota >= 3.5 THEN '✅ Aprobó' WHEN s.nota > 0.0 AND s.nota < 3.5 THEN '❌ Reprobó' ELSE '⏳ Pendiente' END AS "Resultado"
                FROM estudiantes e
                LEFT JOIN seguimiento s ON e.id_estudiante = s.id_estudiante
                LEFT JOIN asignaturas a ON s.codigo_alfa = a.codigo_alfa
                LEFT JOIN malla_curricular m ON a.codigo_alfa = m.codigo_alfa
                ORDER BY e.nombre_completo ASC
            """)
            with engine.connect() as conn:
                df_det = pd.read_sql(query_maestra, conn)
            
            df_det['ID'] = df_det['ID'].astype(str).str.replace(r'\.0$', '', regex=True)
            
            # Aplicamos filtros
            if busqueda:
                df_det = df_det[df_det['Estudiante'].str.contains(busqueda, case=False, na=False) | df_det['ID'].str.contains(busqueda, case=False, na=False)]
            if estado_filtro != "Todos": df_det = df_det[df_det['Resultado'] == estado_filtro]
            if disp_filtro != "Todos": df_det = df_det[df_det['Estado_Malla'] == disp_filtro]

            def color_integral(row):
                estilos = [''] * len(row)
                malla = row['Estado_Malla']
                if malla == 'Construida': estilos[3] = 'background-color: #d4edda; color: #155724; font-weight: bold'
                elif malla == 'En construcción': estilos[3] = 'background-color: #fff3cd; color: #856404; font-weight: bold'
                else: estilos[3] = 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                
                res = row['Resultado']
                if '✅' in res: estilos[4] = 'background-color: #d4edda; border-left: 5px solid green'
                elif '❌' in res: estilos[4] = 'background-color: #f8d7da; border-left: 5px solid red'
                return estilos

            if not df_det.empty:
                st.dataframe(df_det.style.apply(color_integral, axis=1), use_container_width=True, hide_index=True)
            else:
                st.info("Sin registros cargados.")
        except Exception as e:
            st.error(f"Falla en reporte: {e}")

    # --- ZONA DE MANTENIMIENTO (BORRADO EFECTIVO) ---
    st.divider()
    with st.container():
        with st.expander("🛠️ Zona de Mantenimiento y Depuración", expanded=False):
            try:
                with engine.connect() as conn:
                    df_mant = pd.read_sql(text("SELECT id_estudiante, nombre_completo FROM estudiantes ORDER BY nombre_completo"), conn)
                if not df_mant.empty:
                    lista_est = [f"{r['id_estudiante']} - {r['nombre_completo']}" for _, r in df_mant.iterrows()]
                    seleccion_mant = st.selectbox("Seleccione registro para eliminar:", options=lista_est, key="maint_sel_key")
                    
                    if st.button("❌ Eliminar Registro Completo", use_container_width=True, type="primary"):
                        id_del = seleccion_mant.split(" - ")[0]
                        # Eliminación en cascada manual para asegurar borrado físico
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM seguimiento WHERE id_estudiante = :id"), {"id": id_del})
                            conn.execute(text("DELETE FROM estudiantes WHERE id_estudiante = :id"), {"id": id_del})
                        st.success(f"Registro {id_del} eliminado correctamente.")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Base de datos de estudiantes vacía.")
            except:
                st.info("Inicie el sistema registrando al primer estudiante.")