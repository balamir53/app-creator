from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import users, items, langgraph, react_native_builder

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI project"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(langgraph.router, prefix="/api/v1/ai", tags=["ai", "langgraph"])
app.include_router(react_native_builder.router, prefix="/api/v1/mobile", tags=["mobile", "react-native"])


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}