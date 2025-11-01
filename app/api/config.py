import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega as variáveis de ambiente do arquivo .env na raiz do projeto.
load_dotenv()


class Settings:
    """
    Configuração do banco vinda do ambiente.
    Preferência:
    1) DATABASE_URL (se existir)
    2) Variáveis padrão de provedores (PG*)
    3) Variáveis customizadas (POSTGRES_*)
    """

    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        # Preferir PG* (Railway/Cloud) e só depois POSTGRES_*
        POSTGRES_USER: str = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or ""
        POSTGRES_PASSWORD_RAW: str = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
        POSTGRES_DB: str = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or ""
        POSTGRES_SERVER: str = os.getenv("PGHOST") or os.getenv("POSTGRES_SERVER") or "localhost"
        POSTGRES_PORT: str = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432"

        ENCODED_PASSWORD = quote_plus(POSTGRES_PASSWORD_RAW)
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{ENCODED_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

        # SSL opcional: se o provedor exigir, defina DB_SSLMODE=require nas envs
        DB_SSLMODE = os.getenv("DB_SSLMODE") or os.getenv("PGSSLMODE")
        if DB_SSLMODE and "sslmode=" not in DATABASE_URL:
            sep = "&" if "?" in DATABASE_URL else "?"
            DATABASE_URL = f"{DATABASE_URL}{sep}sslmode={DB_SSLMODE}"


settings = Settings()
