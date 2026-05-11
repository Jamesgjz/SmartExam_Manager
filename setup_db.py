import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def crear_tablas():
    # SQL robustecido para cubrir todo el proceso académico de UNIMINUTO
    comandos = [
        # 1. TABLA DE ASIGNATURAS (Malla)
        """
        CREATE TABLE IF NOT EXISTS asignaturas (
            codigo_alfa VARCHAR(20) PRIMARY KEY,
            nombre_asignatura VARCHAR(150) NOT NULL,
            periodo INT,
            momento VARCHAR(10),
            estado_construccion VARCHAR(50) DEFAULT 'Sin Iniciar' -- Sin Iniciar, En proceso, Creada, etc.
        )
        """,
        # 2. TABLA DE DOCENTES (Para el registro de profesores que evalúan/califican)
        """
        CREATE TABLE IF NOT EXISTS docentes (
            id_docente SERIAL PRIMARY KEY,
            nombre_completo VARCHAR(150) NOT NULL,
            area_facultad VARCHAR(100)
        )
        """,
        # 3. TABLA DE ESTUDIANTES
        """
        CREATE TABLE IF NOT EXISTS estudiantes (
            id_estudiante VARCHAR(20) PRIMARY KEY,
            nombre_completo VARCHAR(150) NOT NULL,
            correo VARCHAR(100),
            estado_matricula VARCHAR(50) -- Matriculado, Admitido, etc.
        )
        """,
        # 4. TABLA DE SEGUIMIENTO Y RESULTADOS (El corazón de la automatización)
        """
        CREATE TABLE IF NOT EXISTS seguimiento (
            id SERIAL PRIMARY KEY,
            id_estudiante VARCHAR(20) REFERENCES estudiantes(id_estudiante),
            codigo_alfa VARCHAR(20) REFERENCES asignaturas(codigo_alfa),
            fecha_notificacion DATE,
            fecha_examen DATE,
            hora_examen TIME,
            enlace_teams TEXT,
            profesor_evalua VARCHAR(150),
            profesor_califica VARCHAR(150),
            asistencia BOOLEAN DEFAULT FALSE,
            nota DECIMAL(3,2) DEFAULT 0.0,
            resultado VARCHAR(20), -- Aprobado / Reprobado
            observaciones TEXT
        )
        """
    ]
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        for cmd in comandos:
            cur.execute(cmd)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ ¡Estructura de SmartExam Manager (v2.2) creada exitosamente!")
    except Exception as e:
        print(f"❌ Error al crear la estructura: {e}")

if __name__ == "__main__":
    crear_tablas()