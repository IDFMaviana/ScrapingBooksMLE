from fastapi import FastAPI

app= FastAPI(title ="API de Livros",
             description="API para consultar dados de livro extraidos do site books.toscrape.com",
             version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Livros!"}