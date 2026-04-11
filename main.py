import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine
import models
from routers import items, customers, bills, settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BillEase API",
    description="GST Billing System",
    version="1.1.0",
)

# CORS — read from environment variable
# Set ALLOWED_ORIGINS in Koyeb dashboard after frontend deploy
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = ["*"] if allowed_origins_env == "*" else [
    o.strip() for o in allowed_origins_env.split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ────────────────────────────────────────────────
app.include_router(items.router)
app.include_router(customers.router)
app.include_router(bills.router)
app.include_router(settings.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "BillEase API is running", "docs": "/docs"}
