import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def actualizar_tabla():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        # Añadimos la columna para guardar el nombre original del Excel si no hay match
        cur.execute("ALTER TABLE seguimiento ADD COLUMN IF NOT EXISTS materia_pendiente VARCHAR(255);")
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Columna 'materia_pendiente' añadida con éxito.")
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")

if __name__ == "__main__":
    actualizar_tabla()