import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

def migrar_datos():
    excel_file = 'Organización por prioridad.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ No encuentro el archivo {excel_file}. Asegúrate de que esté en la carpeta.")
        return

    print("Reading Excel sheets...")
    
    # 1. Migrar Estudiantes desde la pestaña 'Lista'
    df_lista = pd.read_excel(excel_file, sheet_name='Lista')
    # Limpiamos los datos: tomamos solo las columnas que nos sirven y quitamos vacíos
    estudiantes = df_lista[['ID', 'NOMBRES Y APELLIDOS', 'CORREO', 'PROGRAMA', 'OBSERVACIÓN 2// 06 - 06-2005']].copy()
    estudiantes.columns = ['id_estudiante', 'nombre_completo', 'correo', 'programa', 'estado_matricula']
    estudiantes = estudiantes.dropna(subset=['id_estudiante']) # Quitamos filas sin ID
    
    # 2. Migrar Malla desde la pestaña 'Malla'
    df_malla = pd.read_excel(excel_file, sheet_name='Malla')
    # La malla tiene una estructura doble, tomamos la primera parte
    malla = df_malla[['ALFA', 'NOMBRE CURSO', 'PERIODO', 'MOMENTO']].copy()
    malla.columns = ['codigo_alfa', 'nombre_asignatura', 'periodo', 'momento']
    malla = malla.dropna(subset=['codigo_alfa'])

    try:
        # Insertar en la base de datos
        print("Inserting students...")
        estudiantes.to_sql('estudiantes', engine, if_exists='append', index=False)
        
        print("Inserting courses...")
        malla.to_sql('asignaturas', engine, if_exists='append', index=False)
        
        print("✅ ¡Migración exitosa! Los datos ya están en PostgreSQL.")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    migrar_datos()