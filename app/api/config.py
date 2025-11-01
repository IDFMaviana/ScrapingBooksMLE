import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega as variáveis de ambiente do arquivo .env na raiz do projeto.
load_dotenv()


class Settings:
    """
    Classe para armazenar as configurações carregadas do ambiente.
    - Preferimos a variável única DATABASE_URL quando fornecida (Railway/Render).
    - Caso contrário, montamos a URL usando POSTGRES_* ou, em fallback, PG* do provedor.
    """

    # 1) Preferir DATABASE_URL se presente (e.g., Railway/Render)
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        POSTGRES_USER: str = os.getenv("POSTGRES_USER") or os.getenv("PGUSER") or ""
        POSTGRES_PASSWORD_RAW: str = os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD") or ""
        POSTGRES_DB: str = os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE") or ""
        # Evita host vazio (que força socket local). Prioriza POSTGRES_SERVER, depois PGHOST.
        POSTGRES_SERVER: str = (os.getenv("POSTGRES_SERVER") or os.getenv("PGHOST") or "localhost")
        POSTGRES_PORT: str = (os.getenv("POSTGRES_PORT") or os.getenv("PGPORT") or "5432")

        ENCODED_PASSWORD = quote_plus(POSTGRES_PASSWORD_RAW)
        DATABASE_URL = (
            f"postgresql://{POSTGRES_USER}:{ENCODED_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )


settings = Settings()
