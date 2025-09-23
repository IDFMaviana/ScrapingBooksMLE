import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega as variáveis de ambiente do arquivo .env que está na raiz do projeto.
load_dotenv()

class Settings:
    """
    Classe para armazenar as configurações carregadas do ambiente.
    """
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    # O nome do host 'db' corresponde ao nome do serviço no docker-compose.yml
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db") 
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    ENCODED_PASSWORD = quote_plus(POSTGRES_PASSWORD)

    # Monta a URL de conexão do banco de dados a partir das variáveis
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{ENCODED_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

settings = Settings()
