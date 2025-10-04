This is a FastAPI project workspace with the following structure:

## Project Structure
```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   └── database.py        # Database configuration
├── models/
│   ├── __init__.py
│   └── models.py          # SQLAlchemy models
├── routers/
│   ├── __init__.py
│   ├── items.py           # Items endpoints
│   └── users.py           # Users endpoints
├── schemas/
│   ├── __init__.py
│   ├── item.py            # Pydantic schemas for items
│   └── user.py            # Pydantic schemas for users
└── services/
    ├── __init__.py
    ├── item_service.py     # Business logic for items
    └── user_service.py     # Business logic for users
tests/                      # Test files
alembic/                   # Database migrations
requirements.txt           # Python dependencies
.env.example              # Environment variables template
```

## Running the Project
- Development server: Use the "Run FastAPI Dev Server" task or run `uvicorn app.main:app --reload`
- API documentation: http://localhost:8000/docs
- The project uses SQLAlchemy for database operations and Pydantic for data validation