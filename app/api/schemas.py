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
# schema para a estatistica
class CategoryStatsSchema(BaseModel):
    category_name: str
    book_count: int
    average_price: float

    class Config:
        from_attributes = True

class HealthCheckResponse(BaseModel):
    api_status: str
    db_status: str

# Estatísticas gerais (overview)
class RatingDistributionSchema(BaseModel):
    one: int
    two: int
    three: int
    four: int
    five: int

    class Config:
        from_attributes = True

class OverviewStatsSchema(BaseModel):
    total_books: int
    average_price: float
    rating_distribution: RatingDistributionSchema

    class Config:
        from_attributes = True

# Estatísticas detalhadas por categoria
class CategoryDetailStatsSchema(BaseModel):
    category_name: str
    book_count: int
    average_price: float
    min_price: float
    max_price: float

    class Config:
        from_attributes = True

# -----------------------------
# Schemas para consumo de modelos ML
# -----------------------------

class MLFeatureSchema(BaseModel):
    book_id: int
    price: float
    rating: int
    category_id: int

    class Config:
        from_attributes = True


class MLTrainingRowSchema(BaseModel):
    book_id: int
    title: str
    price: float
    rating: int
    category_name: str

    class Config:
        from_attributes = True


class MLPredictionIn(BaseModel):
    book_id: int
    prediction: float
    model: str | None = None


class MLPredictionsIn(BaseModel):
    items: list[MLPredictionIn]


class MLPredictionsAck(BaseModel):
    received: int
    status: str
