from pydantic import BaseModel

# Schema para a Categoria (mostra apenas o ID e o nome)
class CategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Schema para o Livro
class BookSchema(BaseModel):
    id: int
    title: str
    price: float
    rating: int
    image_url: str
    
    # aninha o retorno
    category: CategorySchema

    class Config:
        from_attributes = True

class HealthCheckResponse(BaseModel):
    api_status: str
    db_status: str