#Imagem pyhon
FROM python:3.12-slim 

#Define o direotiro do container
WORKDIR /app

# Copia apenas o requirements.txt primeiro (melhora cache do Docker)
COPY requirements.txt .

# Dependencias python
RUN pip install --no-cache-dir -r requirements.txt

#
COPY . .    

# Unicorn para rodar o fastAPI
CMD ["unicorn","api.main:app","--host","0.0.0.0","--port","8000"]
