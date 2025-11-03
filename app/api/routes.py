from fastapi import APIRouter, Depends, HTTPException, Query
from . import models, schemas
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, func
from typing import List, Optional

router = APIRouter()
from .database import get_db


@router.get(
    "/api/v1/books",
    tags=["books"],
    response_model=List[schemas.BookSchema]
)
def get_books(db: Session = Depends(get_db)):
    query = db.query(models.books)
    query_com_category = query.options(joinedload(models.books.category))
    books = query_com_category.all()
    return books


@router.get(
    "/api/v1/books/search",
    tags=["Books"],
    response_model=List[schemas.BookSchema]
)
def get_pesquisa_books(
    title: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.books).options(joinedload(models.books.category))

    if title:
        query = query.filter(models.books.title.ilike(f"%{title}%"))
    if category:
        query = (
            query.join(models.Category)
            .filter(models.Category.name.ilike(f"%{category}%"))
        )

    books = query.all()
    return books


@router.get(
    "/api/v1/categories",
    tags=["Category"],
    response_model=List[schemas.CategorySchema]
)
def get_categories(db: Session = Depends(get_db)):
    query = db.query(models.Category)
    books = query.all()
    return books


@router.get(
    "/api/v1/books/stats",
    tags=["Books"],
    response_model=List[schemas.CategoryStatsSchema]
)
def get_book_stat(db: Session = Depends(get_db)):
    stats_query = (
        db.query(
            models.Category.name.label("category_name"),
            func.count(models.books.id).label("book_count"),
            func.avg(models.books.price).label("average_price"),
        )
        .join(models.books, models.Category.id == models.books.category_id)
        .group_by(models.Category.name)
        .order_by(models.Category.name)
    )
    results = stats_query.all()
    return results


# Rotas específicas de /books devem vir antes da rota dinâmica /books/{book_id}
@router.get(
    "/api/v1/books/top-rated",
    tags=["books"],
    response_model=List[schemas.BookSchema]
)
def get_top_rated_books(limit: int = 10, db: Session = Depends(get_db)):
    query = (
        db.query(models.books)
        .options(joinedload(models.books.category))
        .order_by(models.books.rating.desc(), models.books.title.asc())
        .limit(limit)
    )
    books = query.all()
    return books


@router.get(
    "/api/v1/books/price-range",
    tags=["books"],
    response_model=List[schemas.BookSchema]
)
def get_books_por_faixa_preco(
    price_min: Optional[float] = Query(None, alias="min"),
    price_max: Optional[float] = Query(None, alias="max"),
    db: Session = Depends(get_db),
):
    query = db.query(models.books).options(joinedload(models.books.category))
    if price_min is not None:
        query = query.filter(models.books.price >= price_min)
    if price_max is not None:
        query = query.filter(models.books.price <= price_max)
    books = query.order_by(models.books.price.asc()).all()
    return books


@router.get(
    "/api/v1/books/{book_id}",
    tags=["books"],
    response_model=schemas.BookSchema
)
def get_book_pelo_id(book_id: int, db: Session = Depends(get_db)):
    book = (
        db.query(models.books)
        .options(joinedload(models.books.category))
        .filter(models.books.id == book_id)
        .first()
    )
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book


@router.get(
    "/api/v1/health",
    tags=["Health Check"],
    response_model=schemas.HealthCheckResponse
)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        print(f"Health check da base de dados falhou: {e}")
        db_status = "error"

    return {"api_status": "ok", "db_status": db_status}


# -----------------------------
# Endpoints de Insights/Estatísticas
# -----------------------------

@router.get(
    "/api/v1/stats/overview",
    tags=["Stats"],
    response_model=schemas.OverviewStatsSchema
)
def get_stats_overview(db: Session = Depends(get_db)):
    total = db.query(models.books.id).count()
    avg_price = db.query(func.avg(models.books.price)).scalar() or 0.0

    rating_rows = (
        db.query(models.books.rating, func.count(models.books.id))
        .group_by(models.books.rating)
        .all()
    )
    dist_map = {r: 0 for r in [1, 2, 3, 4, 5]}
    for r, c in rating_rows:
        if r in dist_map:
            dist_map[r] = c

    return {
        "total_books": total,
        "average_price": float(avg_price),
        "rating_distribution": {
            "one": dist_map[1],
            "two": dist_map[2],
            "three": dist_map[3],
            "four": dist_map[4],
            "five": dist_map[5],
        },
    }


@router.get(
    "/api/v1/stats/categories",
    tags=["Stats"],
    response_model=List[schemas.CategoryDetailStatsSchema]
)
def get_stats_categories(db: Session = Depends(get_db)):
    stats_query = (
        db.query(
            models.Category.name.label("category_name"),
            func.count(models.books.id).label("book_count"),
            func.avg(models.books.price).label("average_price"),
            func.min(models.books.price).label("min_price"),
            func.max(models.books.price).label("max_price"),
        )
        .join(models.books, models.Category.id == models.books.category_id)
        .group_by(models.Category.name)
        .order_by(models.Category.name)
    )
    rows = stats_query.all()
    return rows


# -----------------------------
# Endpoints para consumo de modelos ML
# -----------------------------

@router.get(
    "/api/v1/ml/features",
    tags=["ML"],
    response_model=List[schemas.MLFeatureSchema]
)
def get_ml_features(limit: int = 500, offset: int = 0, db: Session = Depends(get_db)):
    query = (
        db.query(models.books)
        .options(joinedload(models.books.category))
        .order_by(models.books.id.asc())
        .offset(offset)
        .limit(limit)
    )
    rows = query.all()
    feats = [
        {
            "book_id": r.id,
            "price": float(r.price) if r.price is not None else 0.0,
            "rating": int(r.rating) if r.rating is not None else 0,
            "category_id": int(r.category_id) if r.category_id is not None else 0,
        }
        for r in rows
    ]
    return feats


@router.get(
    "/api/v1/ml/training-data",
    tags=["ML"],
    response_model=List[schemas.MLTrainingRowSchema]
)
def get_ml_training_data(limit: int = 500, offset: int = 0, db: Session = Depends(get_db)):
    query = (
        db.query(models.books)
        .options(joinedload(models.books.category))
        .order_by(models.books.id.asc())
        .offset(offset)
        .limit(limit)
    )
    rows = query.all()
    data = [
        {
            "book_id": r.id,
            "title": r.title,
            "price": float(r.price) if r.price is not None else 0.0,
            "rating": int(r.rating) if r.rating is not None else 0,
            "category_name": r.category.name if r.category else None,
        }
        for r in rows
    ]
    return data


@router.post(
    "/api/v1/ml/predictions",
    tags=["ML"],
    response_model=schemas.MLPredictionsAck
)
def post_ml_predictions(payload: schemas.MLPredictionsIn, db: Session = Depends(get_db)):
    # Endpoint para receber predições de modelos externos.
    # Nesta versão, apenas acusamos recebimento para fins de integração.
    received = len(payload.items) if payload and payload.items else 0
    return {"received": received, "status": "ok"}
