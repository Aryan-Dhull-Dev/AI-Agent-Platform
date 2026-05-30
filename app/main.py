from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.db.session import engine, Base
from app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Close connections
    await engine.dispose()


app = FastAPI(
    title="AI Agent Platform",
    description="Cloud-native AI agent orchestration platform",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "ok", "message": "AI Agent Platform is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to AI Agent Platform", "docs": "/docs"}


@app.get("/test-db")
async def test_database():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()

            return {
                "status": "database_connected",
                "query_result": row[0]
            }

    except Exception as e:
        return {
            "status": "database_error",
            "error": str(e)
        }