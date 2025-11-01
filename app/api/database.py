from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
from .config import settings


def _normalize_dsn(dsn: str) -> str:
    """Normalize DSN for SQLAlchemy 2.x (postgres -> postgresql)."""
    if dsn and dsn.startswith("postgres://"):
        return dsn.replace("postgres://", "postgresql://", 1)
    return dsn


SQLALCHEMY_DATABASE_URL = _normalize_dsn(settings.DATABASE_URL or "")

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não configurada. Defina DATABASE_URL ou as variáveis PG*/POSTGRES_*"
    )

# Log conciso do alvo de conexão (sem segredos)
try:
    parsed = urlparse(SQLALCHEMY_DATABASE_URL)
    host_info = f"{parsed.hostname}:{parsed.port} / db={parsed.path.lstrip('/')}"
    print(f"[DB] Conectando em {host_info}")
except Exception:
    pass

# Engine com pre-ping para recuperar conexões interrompidas
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa
Base = declarative_base()


def get_db():
    """Helper para obter/fechar sessão por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

