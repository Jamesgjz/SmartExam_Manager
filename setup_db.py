import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def crear_tablas():
    # SQL basado en tus necesidades de seguimiento y malla
    comandos = [
        """
        CREATE TABLE IF NOT EXISTS estudiantes (
            id_estudiante VARCHAR(20) PRIMARY KEY,
            nombre_completo VARCHAR(150) NOT NULL,
            correo VARCHAR(100),
            programa VARCHAR(100),
            estado_matricula VARCHAR(50)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS asignaturas (
            codigo_alfa VARCHAR(20) PRIMARY KEY,
            nombre_asignatura VARCHAR(150) NOT NULL,
            periodo INT,
            momento VARCHAR(10)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS seguimiento (
            id SERIAL PRIMARY KEY,
            id_estudiante VARCHAR(20) REFERENCES estudiantes(id_estudiante),
            codigo_alfa VARCHAR(20) REFERENCES asignaturas(codigo_alfa),
            fecha_citacion DATE,
            hora_citacion TIME,
            enlace_teams TEXT,
            nota DECIMAL(3,2),
            asistencia BOOLEAN DEFAULT FALSE,
            estado_pago BOOLEAN DEFAULT FALSE
        )
        """
    ]
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        cur = conn.cursor()
        for cmd in comandos:
            cur.execute(cmd)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ ¡Estructura de SmartExam Manager creada exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    crear_tablas()