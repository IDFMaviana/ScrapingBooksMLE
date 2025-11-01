import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.api.database import SessionLocal,engine
from app.api import models
from dotenv import load_dotenv
from urllib.parse import urljoin


load_dotenv()

BASE_URL: str = os.getenv("URL_TO_SCRAPE")


models.Base.metadata.create_all(bind=engine)

def scrape_books():
    db = SessionLocal()
    print("Iniciando o Scraping")
    #Define mapeamento das avaliações
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}

    page = requests.get(BASE_URL)

    if page.status_code == 200:
        # --- FASE 1: RASPAGEM E CRIAÇÃO DAS CATEGORIAS ---
        print("\n--- Fase 1: Encontrando e salvando categorias ---")
        soup = BeautifulSoup(page.content,"html.parser")
        lista_categoria = soup.find('ul',class_='nav-list')
        item_categoria = lista_categoria.find('ul').find_all('li')
        
        for item in item_categoria:
            link = item.find('a')
            nome_categoria = link.get_text().strip()
            url_categoria = urljoin(BASE_URL,link.get('href'))
            #Verifica se a categoria ja existe
            categoria_existentes = db.query(models.Category).filter_by(name=nome_categoria).first()
            if not categoria_existentes:
                nova_categoria = models.Category(name=nome_categoria, url=url_categoria)
                db.add(nova_categoria)
        #commmit transação        
        db.commit()
        print(f"{len(item_categoria)} categorias salvas/verificadas com sucesso.")
    
    # --- FASE 2: Livros associados a categorias ---
        print("\n--- Fase 2: Raspando livros de cada categoria ---")
        todas_categorias = db.query(models.Category).all()
        livros_adicionados = 0

    for categoria in todas_categorias:
        page = requests.get(categoria.url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content,"html.parser")
            #encontra os livros na pagina de categoria
            book_container = soup.find_all('article',class_='product_pod')
            for book_name in book_container:
                #titulo
                title_element = book_name.find('h3').find('a')
                title = title_element['title']
                #Preço
                price_element = book_name.find('p',class_='price_color')
                price = float(price_element.get_text().replace('£',''))
                # rating
                rating_element = book_name.find('p',class_='star-rating')
                rating_text = rating_element['class'][1]
                rating = rating_map.get(rating_text,0)
                # URL da Imagem
                image_element = book_name.find('div',class_='image_container').find('img')
                relative_image_url = image_element['src']
                image_url = urljoin(BASE_URL, relative_image_url)
                
                existing = db.query(models.books).filter_by(title=title, category_id=categoria.id).first()
                if existing:
                    existing.price = price
                    existing.rating = rating
                    existing.image_url = image_url
                else:
                    novo_livro = models.books(title=title,
                                              price = price,
                                              rating = rating,
                                              image_url = image_url,
                                              category_id = categoria.id)
                    db.add(novo_livro)
                    livros_adicionados += 1
        print(f"\nAdicionando {livros_adicionados} livros à base de dados...")
        db.commit()
        print("Livros salvos com sucesso!")
    else:
       print(f"Erro ao carregar a pagina, código do status: {page.status_code}")
    
    print("processo finalizado")

    db.close()

#if __name__ == "__main__":
#    scrape_books()
