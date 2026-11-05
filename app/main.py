from fastapi import FastAPI

# Create the FastAPI application
app = FastAPI(
    title="Smart Inventory System",
    description="Inventory management and stockout prediction API",
    version="1.0.0"
)


# First API endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Smart Inventory System!",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Smart Inventory System"
    }