import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Leiriarte API", description="Backend for Leiriarte e‑commerce")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Leiriarte backend is running"}


@app.get("/test")
def test_database():
    info = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "collections": []
    }
    try:
        if db is not None:
            info["database"] = "✅ Connected"
            info["database_url"] = "✅ Set"
            info["database_name"] = getattr(db, 'name', 'unknown')
            try:
                info["collections"] = db.list_collection_names()
            except Exception as e:
                info["collections"] = [f"error: {str(e)[:80]}"]
        else:
            info["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        info["database"] = f"❌ Error: {str(e)[:80]}"
    info["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    info["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return info


# ---------- Catalog Endpoints ----------
@app.get("/api/products", response_model=List[Product])
def list_products(category: Optional[str] = None, featured: Optional[bool] = None):
    query = {}
    if category:
        query["category"] = category
    if featured is not None:
        query["featured"] = featured
    docs = get_documents("product", query)
    # Map Mongo docs to Product by selecting fields
    products: List[Product] = []
    for d in docs:
        products.append(Product(
            title=d.get("title", ""),
            description=d.get("description"),
            price=float(d.get("price", 0)),
            category=d.get("category", "Custom"),
            materials=list(d.get("materials", [])),
            techniques=list(d.get("techniques", [])),
            images=list(d.get("images", [])),
            customizable=bool(d.get("customizable", True)),
            featured=bool(d.get("featured", False)),
            in_stock=bool(d.get("in_stock", True)),
        ))
    return products


@app.post("/api/products", status_code=201)
def create_product(product: Product):
    try:
        create_document("product", product)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Orders ----------
@app.post("/api/orders", status_code=201)
def create_order(order: Order):
    try:
        create_document("order", order)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
