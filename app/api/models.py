from sqlalchemy import Column,Integer,String,Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Category(Base):
    #Nome da tabela:
    __tablename__ = "categories"
    #Colunas
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    url = Column(String(255))
    
    # Cria a relação
    books = relationship("books", back_populates="category")

class books(Base):
    #Nome da tabela:
    __tablename__ = "books"
    #Colunas
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    product_description = Column(String(4000))
    price = Column(Float)
    rating = Column(Integer)
    image_url = Column(String(255))
    #category = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Cria a relação
    category = relationship("Category", back_populates="books")