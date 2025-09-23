from fastapi import FastAPI
from . import routes,models
from .database import engine,Base

Base.metadata.create_all(bind=engine)

app= FastAPI(title ="API de Livros",
             description="API para consultar dados de livro extraidos do site books.toscrape.com",
             version="1.0.0")

#Inclui o Router na aplicação
app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Livros!"}