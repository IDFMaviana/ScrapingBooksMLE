# backend/app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Cria a URL de conexão para o SQLAlchemy a partir das configurações
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Cria a engine do SQLAlchemy.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Cria uma classe SessionLocal. Cada instância de SessionLocal será uma sessão de base de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Retorna uma classe que servirá como base para nossas classes de modelo de ORM (em models.py).
Base = declarative_base()

#Helper para obter uma sessao na base
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()