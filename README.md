# Cinema API Service

Cinema API Service is a Django-based RESTful API for managing theatre-related data: plays, performances, actors, genres, theatre halls, and reservations (tickets). It provides endpoints to create, update, and retrieve data, plus JWT authentication and interactive API documentation.

## Table of Contents
- Introduction
- Features
- Requirements
- Installation (Git)
- Environment Variables
- Run Locally
- Run with Docker
- Authentication (JWT)
- API Documentation
- Available Endpoints
- Pagination

## Introduction
This project streamlines the management of theatre data and user interactions. It’s suitable for learning Django REST Framework, building reservation systems, or serving as a backend foundation for theatre/cinema apps.

## Features
- JWT authentication (obtain and refresh tokens)
- Email/username-based login (standard Django user)
- Pagination for list endpoints
- Interactive API docs (Swagger UI and ReDoc)
- CRUD for:
  - Actors
  - Genres
  - Theatre halls
  - Plays
  - Performances
  - Reservations and tickets
- Automatic ticket generation per performance based on hall layout

## Requirements
- Python 3.13+
- PostgreSQL (for local non-Docker runs)
- Docker and Docker Compose (for containerized runs)
- virtualenv

## Installation (Git)
1. Clone the repository:
   - git clone <your-repo-url>
   - cd <project-folder>

2. Create and activate a virtual environment:
   - python -m venv venv  
   - macOS/Linux: `source venv/bin/activate`  
   - Windows: `venv\Scripts\activate`

3. Install dependencies:
   - pip install -r requirements.txt

4. Create a `.env` file (see below) and configure your environment variables.

## Environment Variables
Create a `.env` in the project root and set variables as needed:

Django:
- SECRET_KEY=your_secret_key
- DEBUG=True
- ALLOWED_HOSTS=127.0.0.1,localhost

Database:
- POSTGRES_DB=cinema
- POSTGRES_USER=cinema
- POSTGRES_PASSWORD=cinema
- POSTGRES_HOST=localhost        # use 'db' when running via Docker
- POSTGRES_PORT=5432
- PGDATA=/var/lib/postgresql/data # used by the DB container

Optional (for automated superuser creation in Docker workflows):
- DJANGO_SUPERUSER_USERNAME=admin
- DJANGO_SUPERUSER_EMAIL=admin@example.com
- DJANGO_SUPERUSER_PASSWORD=admin

## Run Locally
1. Apply migrations:
   - python manage.py makemigrations
   - python manage.py migrate

2. (Optional) Create a superuser:
   - python manage.py createsuperuser

3. Run the development server:
   - python manage.py runserver  
   App will be available at http://127.0.0.1:8000/

## Run with Docker
Ensure Docker and Docker Compose are installed.

- Build and start:
  - docker-compose build
  - docker-compose up

Useful commands:
- Stop: `docker-compose down`
- Run in background: `docker-compose up -d`
- Logs: `docker-compose logs -f`

The app will be available at http://localhost:8000/

## Authentication (JWT)
- Obtain access/refresh tokens: POST `/api/auth/jwt/`
- Refresh access token: POST `/api/auth/jwt/refresh/`

Use the created Django user (via createsuperuser or admin) to authenticate.  
Authorization header for protected endpoints:
- Authorization: Bearer <access_token>

## API Documentation
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

## Available Endpoints
Base path: `/api/`
- `/actors/` — list, retrieve, create, update, delete
- `/genres/` — list, retrieve, create, update, delete
- `/halls/` — list, retrieve, create, update, delete
- `/plays/` — list, retrieve, create, update, delete
- `/performances/` — list, retrieve, create, update, delete
- `/reservations/` — list user reservations, create reservation for seats

Note: write operations generally require admin permissions, while reservations require authentication.

## Pagination
All list endpoints support page-number pagination:
- Query params:
  - `page` — page number
  - `page_size` — items per page (up to 100)
