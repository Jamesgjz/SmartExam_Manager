from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Asignatura(Base):
    __tablename__ = 'asignaturas'
    
    id = Column(Integer, primary_key=True)
    codigo_alfa = Column(String(20), unique=True, nullable=False)  # Ej: ISOF V003
    nombre_asignatura = Column(String(200), nullable=False)         # Ej: Introducción a la Ingeniería
    periodo = Column(Integer, nullable=True)                       # Ej: 1, 2, 3...

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    
    id = Column(Integer, primary_key=True)
    documento = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)