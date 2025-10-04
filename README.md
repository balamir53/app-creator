# FastAPI Project with LangGraph AI Integration

A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. Now enhanced with LangGraph for building sophisticated AI workflows and conversational agents.

## Features

- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase the speed to develop features by about 200% to 300%
- **Fewer bugs**: Reduce about 40% of human (developer) induced errors
- **Intuitive**: Great editor support with auto-completion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation
- **🤖 AI-Powered**: Integrated LangGraph workflows for conversational AI and complex task automation

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

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-project
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Database Setup

This project uses SQLAlchemy with Alembic for database migrations.

1. Initialize Alembic (if not already done):
```bash
alembic init alembic
```

2. Create a migration:
```bash
alembic revision --autogenerate -m "Initial migration"
```

3. Run migrations:
```bash
alembic upgrade head
```

## API Endpoints

### Core Endpoints
### Items
- `GET /api/v1/items` - Get all items
- `GET /api/v1/items/{item_id}` - Get item by ID
- `POST /api/v1/items` - Create new item
- `PUT /api/v1/items/{item_id}` - Update item
- `DELETE /api/v1/items/{item_id}` - Delete item

### Users
- `GET /api/v1/users` - Get all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### 🤖 AI Endpoints (LangGraph)
- `POST /api/v1/ai/chat` - Conversational AI with memory
- `POST /api/v1/ai/workflow/task` - Complex multi-step task execution
- `GET /api/v1/ai/conversations/{id}` - Get conversation history
- `DELETE /api/v1/ai/conversations/{id}` - Clear conversation
- `GET /api/v1/ai/health` - AI service health check

> 📖 **Detailed AI Guide**: See [docs/LANGGRAPH_GUIDE.md](docs/LANGGRAPH_GUIDE.md) for complete LangGraph integration documentation.

## Testing

Run tests with pytest:
```bash
pytest
```

## Configuration

Environment variables can be set in `.env` file:

### Core Configuration
- `SECRET_KEY`: Secret key for JWT tokens
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: Application environment (development/production)
- `DEBUG`: Enable debug mode

### 🤖 AI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key for GPT models
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (true/false)
- `LANGCHAIN_API_KEY`: Your LangSmith API key (optional)
- `LANGCHAIN_PROJECT`: Project name for LangSmith tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.