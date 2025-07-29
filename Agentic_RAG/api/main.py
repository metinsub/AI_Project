# FastAPI Application Entry Point   

from fastapi import FastAPI 
from api.routes.health import router as health_router
from api.routes.ingest import router as ingest_router

app = FastAPI()

app.include_router(health_router)
app.include_router(ingest_router)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!!"}


