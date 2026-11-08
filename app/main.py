from fastapi import FastAPI
from app.core.database import get_connection
from app.api.products import router as products_router
from app.api.inventory import router as inventory_router
from app.api.sales import router as sales_router
from app.api.analytics import router as analytics_router
from app.api.predictions import router as predictions_router
from app.api.recommendations import router as recommendations_router
from app.api import suppliers

app = FastAPI(
    title="Smart Inventory System",
    description="Inventory management and stockout prediction API",
    version="1.0.0"
)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(sales_router)
app.include_router(analytics_router)
app.include_router(predictions_router)
app.include_router(recommendations_router)
app.include_router(suppliers.router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Smart Inventory System!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Smart Inventory System"
    }


@app.get("/db-health")
def database_health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()

        return {
            "database": "connected",
            "test_result": result[0]
        }

    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e)
        }
