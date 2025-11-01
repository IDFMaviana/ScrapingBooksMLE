from fastapi import APIRouter, Depends, HTTPException
#import sys
#import os
#sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from . import models, schemas
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, text, func
from typing import List, Optional
router = APIRouter()
from .database import get_db

@router.get("/api/v1/books",
            tags=["books"],
            response_model=List[schemas.BookSchema])
def get_books(db: Session = Depends(get_db)):
    query = db.query(models.books)
    query_com_category = query.options(joinedload(models.books.category))
    books = query_com_category.all()
    return books

@router.get("/api/v1/books/search",
            tags=["Books"],
            response_model=List[schemas.BookSchema])
def get_pesquisa_books(title: Optional[str] = None, 
                       category: Optional[str] = None, 
                       db: Session = Depends(get_db)):
    query = db.query(models.books).options(joinedload(models.books.category))

    if title:
        query = query.filter(models.books.title.ilike(f"%{title}%"))
    if category:
        # Faz filtra atraves de um join
        query = query.join(models.Category).filter(models.Category.name.ilike(f"%{category}%"))
    
    books = query.all()
    
    return books

@router.get("/api/v1/categories",
            tags=["Category"],
            response_model=List[schemas.CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    query = db.query(models.Category)
    books = query.all()
    return books


@router.get("/api/v1/books/stats",
            tags=["Books"],
            response_model=List[schemas.CategoryStatsSchema])
def get_book_stat(db: Session = Depends(get_db)):
    stats_query = db.query(models.Category.name.label("category_name"),
                           func.count(models.books.id).label("book_count"),
                           func.avg(models.books.price).label("average_price")
                           ).join(models.books, models.Category.id == models.books.category_id).group_by(models.Category.name).order_by(models.Category.name) 

    results = stats_query.all()
    return results

@router.get("/api/v1/books/{book_id}",
            tags=["books"],
            response_model=schemas.BookSchema)
def get_book_pelo_id(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.books).options(
        joinedload(models.books.category)
    ).filter(models.books.id == book_id).first()
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

    return {
        "api_status": "ok",
        "db_status": db_status
    }