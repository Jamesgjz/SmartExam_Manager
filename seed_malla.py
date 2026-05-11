from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Credenciales directas (Cópialas de tu consola de Neon)
USER = "neondb_owner"
PASS = "npg_VPz8RYwQ7Gxs"
HOST = "ep-misty-dream-aplxjl8l-pooler.c-7.us-east-1.aws.neon.tech"
NAME = "neondb"

# 2. URL con SSL forzado
url = f"postgresql://{USER}:{PASS}@{HOST}:5432/{NAME}?sslmode=require"
engine = create_engine(url)

Base = declarative_base()

# Definimos el modelo aquí mismo para evitar problemas de importación
class Asignatura(Base):
    __tablename__ = 'asignaturas'
    id = Column(Integer, primary_key=True)
    codigo_alfa = Column(String(20), unique=True)
    nombre_asignatura = Column(String(200))
    periodo = Column(Integer)

# 3. La Malla Completa
malla_uniminuto = [
    {"codigo_alfa": "ISOF V003", "nombre_asignatura": "INTRODUCCION A LA INGENIERIA DE SOFTWARE", "periodo": 1},
    {"codigo_alfa": "ISOF V013", "nombre_asignatura": "FUNDAMENTOS DE PROGRAMACION", "periodo": 1},
    {"codigo_alfa": "ISOF V023", "nombre_asignatura": "CALCULO DIFERENCIAL", "periodo": 1},
    {"codigo_alfa": "ISOF V033", "nombre_asignatura": "ALGEBRA LINEAL", "periodo": 1},
    {"codigo_alfa": "ISOF V043", "nombre_asignatura": "PROGRAMACION ORIENTADA A OBJETOS", "periodo": 2},
    {"codigo_alfa": "ISOF V053", "nombre_asignatura": "ESTRUCTURA DE DATOS", "periodo": 2},
    {"codigo_alfa": "ISOF V063", "nombre_asignatura": "CALCULO INTEGRAL", "periodo": 2},
    {"codigo_alfa": "ISOF V073", "nombre_asignatura": "FISICA MECANICA", "periodo": 2},
    {"codigo_alfa": "ISOF V083", "nombre_asignatura": "BASES DE DATOS I", "periodo": 3},
    {"codigo_alfa": "ISOF V093", "nombre_asignatura": "PROGRAMACION WEB", "periodo": 3},
    {"codigo_alfa": "ISOF V103", "nombre_asignatura": "ESTADISTICA Y PROBABILIDAD", "periodo": 3},
    {"codigo_alfa": "ISOF V113", "nombre_asignatura": "SISTEMAS OPERATIVOS", "periodo": 3},
    {"codigo_alfa": "ISOF V123", "nombre_asignatura": "INGENIERIA DE REQUISITOS", "periodo": 4},
    {"codigo_alfa": "ISOF V133", "nombre_asignatura": "ANALISIS Y DISEÑO DE SISTEMAS", "periodo": 4},
    {"codigo_alfa": "ISOF V143", "nombre_asignatura": "BASES DE DATOS II", "periodo": 4},
    {"codigo_alfa": "ISOF V153", "nombre_asignatura": "REDES DE DATOS", "periodo": 4},
    {"codigo_alfa": "ISOF V163", "nombre_asignatura": "ARQUITECTURA DE SOFTWARE", "periodo": 5},
    {"codigo_alfa": "ISOF V173", "nombre_asignatura": "PRUEBAS DE SOFTWARE", "periodo": 5},
    {"codigo_alfa": "ISOF V183", "nombre_asignatura": "PROCESOS DE SOFTWARE", "periodo": 5},
    {"codigo_alfa": "ISOF V193", "nombre_asignatura": "SEGURIDAD DE LA INFORMACION", "periodo": 5},
    {"codigo_alfa": "ISOF V203", "nombre_asignatura": "GESTION DE PROYECTOS DE SOFTWARE", "periodo": 6},
    {"codigo_alfa": "ISOF V213", "nombre_asignatura": "INTELIGENCIA ARTIFICIAL", "periodo": 6},
    {"codigo_alfa": "ISOF V223", "nombre_asignatura": "ETICA PROFESIONAL", "periodo": 6},
    {"codigo_alfa": "ISOF V233", "nombre_asignatura": "ELECTIVA DE PROFUNDIZACION", "periodo": 6}
]

def run_seed():
    print(f"Conectando directamente a Neon en: {HOST}...")
    try:
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for data in malla_uniminuto:
            existente = session.query(Asignatura).filter_by(codigo_alfa=data["codigo_alfa"]).first()
            if not existente:
                nueva = Asignatura(**data)
                session.add(nueva)
                print(f"✅ Cargado: {data['codigo_alfa']}")
        
        session.commit()
        print("\n🚀 ¡MALLA CARGADA EXITOSAMENTE!")
        session.close()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_seed()