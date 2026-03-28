import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import products, orders, shipments

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")

app = FastAPI(title="Дверной Достык", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(shipments.router)


@app.get("/")
def root():
    return {"message": "Дверной Достык API работает"}
