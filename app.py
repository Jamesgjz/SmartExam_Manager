import streamlit as st
import sys
import os

# 1. CONFIGURACIÓN DE RUTAS (Debe ir al puro inicio)
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

# 2. IMPORTACIÓN DE MÓDULOS
# Importamos el engine y los modelos DESDE la carpeta modules
try:
    from modules.database import engine
    from modules.models import Base  # Importamos directamente la clase Base de models.py
    import modules.dashboard as dash
    import modules.students as stud
    import modules.reports as rep
    import modules.builder as build
    import modules.scheduling as sched
except ImportError as e:
    st.error(f"❌ Error crítico de importación: {e}")
    st.stop()

# 3. CREACIÓN AUTOMÁTICA DE TABLAS EN NEON
# Esto se ejecuta una sola vez al arrancar la app
try:
    # Ahora usamos "Base" directamente porque la importamos arriba
    Base.metadata.create_all(bind=engine)
except Exception as e:
    st.warning(f"Nota sobre las tablas: {e}")
# 4. CONFIGURACIÓN VISUAL
st.set_page_config(
    page_title="SmartExam Manager | UNIMINUTO",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # --- SIDEBAR / MENÚ LATERAL ---
    st.sidebar.markdown("<h1 style='text-align: center; color: #002d72;'>SmartExam</h1>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center;'><b>Profesor:</b> James Jaramillo</p>", unsafe_allow_html=True)
    st.sidebar.divider()

    menu = [
        "1. Registro de Solicitud",
        "2. Programación de Evaluaciones",
        "3. Registro de Resultados",
        "4. Dashboards de Gestión",
        "5. Estado de Construcción (Malla)"
    ]
    
    choice = st.sidebar.radio("Etapas del Proceso:", menu)
    
    st.sidebar.divider()
    st.sidebar.info("Utilice este panel para gestionar el ciclo de vida de las pruebas de suficiencia.")
    st.sidebar.caption("v2.1 - Sistema de Automatización Académica")

    # --- CUERPO PRINCIPAL / ENRUTAMIENTO ---
    if choice == "1. Registro de Solicitud":
        stud.registrar_nueva_solicitud()
        
    elif choice == "2. Programación de Evaluaciones":
        sched.programar_evaluaciones()
        
    elif choice == "3. Registro de Resultados":
        rep.registro_resultados()
        
    elif choice == "4. Dashboards de Gestión":
        dash.mostrar_kpis_reales()
        
    elif choice == "5. Estado de Construcción (Malla)":
        build.estado_construccion_malla()

if __name__ == "__main__":
    main()