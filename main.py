import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import items, customers, bills, settings

# Create all DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BillEase API",
    description="GST Billing System — Items, Customers, Invoices and Settings",
    version="1.1.0",
)

# CORS — reads from ALLOWED_ORIGINS environment variable
# Set this in Render dashboard after Vercel deploy
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

app.include_router(items.router)
app.include_router(customers.router)
app.include_router(bills.router)
app.include_router(settings.router)


@app.get("/")
def root():
    return {"message": "BillEase API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
