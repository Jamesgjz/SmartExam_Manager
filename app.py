import streamlit as st
import sys
import os

# CONFIGURACIÓN DE RUTAS: Forzamos la detección de la carpeta 'modules'
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

# IMPORTACIÓN DE MÓDULOS (Asegúrate de haber guardado los cambios en cada archivo de la carpeta modules)
try:
    import modules.dashboard as dash
    import modules.students as stud
    import modules.reports as rep
    import modules.builder as build
    import modules.scheduling as sched
except ImportError as e:
    st.error(f"❌ Error al cargar los módulos: {e}")
    st.stop()

# Configuración visual de la pestaña
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
        # Llama a la función que tiene el desplegable de materias (Malla)
        stud.registrar_nueva_solicitud()
        
    elif choice == "2. Programación de Evaluaciones":
        # Llama a la función con fechas, horas y asignación de profesores
        sched.programar_evaluaciones()
        
    elif choice == "3. Registro de Resultados":
        # Llama a la lógica de Asistencia y Calificación (Aprobado/Reprobado)
        rep.registro_resultados()
        
    elif choice == "4. Dashboards de Gestión":
        # Llama a las métricas y KPIs
        dash.mostrar_kpis_reales()
        
    elif choice == "5. Estado de Construcción (Malla)":
        # Llama a la gestión de materias y registro de nuevos profesores
        build.estado_construccion_malla()

if __name__ == "__main__":
    main()