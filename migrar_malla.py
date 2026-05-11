import pandas as pd
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrar_malla():
    # 1. Nombre exacto de tu archivo de Excel
    archivo_excel = "Organización por prioridad.xlsx"
    
    if not os.path.exists(archivo_excel):
        print(f"❌ No se encontró el archivo: {archivo_excel}")
        print("Asegúrate de que el Excel esté en la misma carpeta que este script.")
        return

    try:
        print(f"Leyendo la hoja 'Malla' de {archivo_excel}...")
        
        # 2. Leer la hoja específica 'Malla'
        # Nota: Usamos engine='openpyxl' para archivos .xlsx
        df = pd.read_excel(archivo_excel, sheet_name='Malla', engine='openpyxl')
        
        # Limpiar nombres de columnas por si tienen espacios
        df.columns = df.columns.str.strip().str.upper()
        
        # Tu Excel tiene las columnas: ALFA, NOMBRE CURSO, PERIODO, MOMENTO
        # Filtramos solo esas para la base de datos
        df_malla = df[['ALFA', 'NOMBRE CURSO', 'PERIODO', 'MOMENTO']].copy()
        df_malla.columns = ['codigo_alfa', 'nombre_asignatura', 'periodo', 'momento']
        
        # Quitamos filas que no tengan código o nombre
        df_malla = df_malla.dropna(subset=['codigo_alfa', 'nombre_asignatura'])

        # 3. Conexión a PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        print("Insertando asignaturas en la base de datos...")
        contador = 0
        for _, row in df_malla.iterrows():
            cur.execute("""
                INSERT INTO asignaturas (codigo_alfa, nombre_asignatura, periodo, momento)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (codigo_alfa) DO NOTHING;
            """, (row['codigo_alfa'], row['nombre_asignatura'], row['periodo'], row['momento']))
            contador += 1
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ ¡Éxito! Se han cargado {contador} asignaturas desde la pestaña 'Malla'.")

    except Exception as e:
        print(f"❌ Error al procesar el Excel: {e}")

if __name__ == "__main__":
    migrar_malla()