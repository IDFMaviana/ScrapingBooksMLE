# ScrapingBooksMLE

API e scraper para coletar dados do site books.toscrape.com, salvar em PostgreSQL e disponibilizar consultas via FastAPI. O projeto foi organizado para ser simples de rodar localmente ou via Docker Compose.

## Descrição e Arquitetura

- Scraper: usa `requests` e `BeautifulSoup` para extrair categorias e livros a partir da URL informada em `URL_TO_SCRAPE`.
- Persistência: modelos `SQLAlchemy` gravam os dados no PostgreSQL (`categories` e `books`).
- API: `FastAPI` expõe rotas de leitura com filtros e estatísticas.
- Deploy local/Docker: `docker-compose.yml` orquestra `db` (PostgreSQL), `api` (FastAPI/uvicorn) e `scraper` (tarefa de carga).

Fluxo resumido:

1) Scraper coleta categorias e livros → 2) grava no banco → 3) API consulta as tabelas e retorna JSON.

Principais arquivos:

- `app/api/main.py`: instancia o app FastAPI e registra rotas.
- `app/api/routes.py`: endpoints da API.
- `app/api/models.py`: modelos `Category` e `books` (SQLAlchemy).
- `app/api/schemas.py`: esquemas Pydantic (respostas da API).
- `app/api/database.py`: engine e sessão do SQLAlchemy.
- `app/api/config.py`: leitura de variáveis de ambiente e `DATABASE_URL`.
- `app/scripts/scraper.py`: rotina de scraping e carga no banco.
- `docker-compose.yml`: serviços `db`, `api` e `scraper`.

## Instalação e Configuração

Pré‑requisitos (opção local):

- Python 3.12+
- PostgreSQL 14+ (ou compatível)
- `pip` e `venv`

Pré‑requisitos (opção Docker):

- Docker e Docker Compose

Variáveis de ambiente (arquivo `.env` na raiz):

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_SERVER` (padrão: `db` quando usando Docker; para local, algo como `localhost`)
- `POSTGRES_PORT` (padrão: `5432`)
- `URL_TO_SCRAPE` (ex.: `https://books.toscrape.com/`)

Exemplo de `.env`:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=books
POSTGRES_SERVER=db
POSTGRES_PORT=5432
URL_TO_SCRAPE=https://books.toscrape.com/
```

Instalação (ambiente local):

```
python -m venv .venv
./.venv/Scripts/activate            # Windows
# source .venv/bin/activate         # Linux/Mac
pip install -r requirements.txt
```

Garanta que o banco PostgreSQL esteja acessível com as variáveis do seu `.env` e que o database (`POSTGRES_DB`) exista.

## Rotas da API

Base URL (padrão): `http://localhost:8000`

- `GET /` — mensagem de boas‑vindas.
- `GET /api/v1/health` — health check da API e do banco.
- `GET /api/v1/categories` — lista categorias.
- `GET /api/v1/books` — lista livros (inclui objeto `category`).
- `GET /api/v1/books/{book_id}` — detalhe de um livro por id.
- `GET /api/v1/books/search?title={...}&category={...}` — busca por título e/ou categoria (filtros opcionais, `ilike`).
- `GET /api/v1/books/stats` — estatísticas por categoria (`book_count`, `average_price`).

Esquemas de resposta (resumo):

- BookSchema: `{ id, title, price, rating, image_url, category: { id, name } }`
- CategorySchema: `{ id, name }`
- CategoryStatsSchema: `{ category_name, book_count, average_price }`
- HealthCheckResponse: `{ api_status, db_status }`

## Exemplos de Chamadas

Health check:

```
curl http://localhost:8000/api/v1/health
```

Resposta:

```
{
  "api_status": "ok",
  "db_status": "ok"
}
```

Listar categorias:

```
curl http://localhost:8000/api/v1/categories
```

Resposta (exemplo):

```
[
  { "id": 1, "name": "Travel" },
  { "id": 2, "name": "Mystery" }
]
```

Listar livros:

```
curl http://localhost:8000/api/v1/books
```

Resposta (exemplo):

```
[
  {
    "id": 10,
    "title": "A Light in the Attic",
    "price": 51.77,
    "rating": 3,
    "image_url": "https://books.toscrape.com/media/cache/xx.jpg",
    "category": { "id": 2, "name": "Poetry" }
  }
]
```

Buscar livros por título e/ou categoria:

```
curl "http://localhost:8000/api/v1/books/search?title=light&category=poetry"
```

Detalhe de um livro:

```
curl http://localhost:8000/api/v1/books/10
```

Estatísticas por categoria:

```
curl http://localhost:8000/api/v1/books/stats
```

Resposta (exemplo):

```
[
  { "category_name": "Poetry", "book_count": 19, "average_price": 35.42 },
  { "category_name": "Travel", "book_count": 11, "average_price": 42.10 }
]
```

## Como Executar

Opção 1 — Docker Compose (recomendado para começar):

```
# 1) Suba o banco
docker compose up -d db

# 2) Rode o scraper para popular as tabelas
docker compose run --rm scraper

# 3) Suba a API
docker compose up -d api

# A API ficará disponível em http://localhost:8000
# Documentação interativa: http://localhost:8000/docs
```

Também é possível subir tudo de uma vez com `docker compose up -d`, mas rodar o scraper como passo explícito facilita ver os logs da coleta.

Opção 2 — Ambiente local (sem Docker):

1) Configure o `.env` e garanta o PostgreSQL acessível.
2) Crie o ambiente e instale dependências (vide seção de instalação).
3) Crie as tabelas (a API cria ao iniciar) e rode o scraper:

```
python -m app.scripts.scraper
```

4) Inicie a API (uvicorn):

```
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

5) Acesse `http://localhost:8000/docs` para testar as rotas.

## Notas

- O serviço `api` no `docker-compose.yml` já usa `uvicorn` e aguarda o banco estar saudável antes de iniciar.
- O pacote `pgvector` está presente na imagem do banco para possíveis evoluções; não é exigido pelas rotas atuais.
- Certos caracteres especiais do site podem aparecer com codificações diferentes dependendo do terminal; isso não afeta a funcionalidade.
