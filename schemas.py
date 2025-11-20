"""
Database Schemas for Leiriarte E‑commerce

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class Product(BaseModel):
    """
    Collection: product
    Represents a customizable product Leiriarte offers
    """
    title: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Detailed description")
    price: float = Field(..., ge=0, description="Base price in EUR")
    category: str = Field(..., description="Category, e.g., 'Wood', 'Acrylic', 'Metal', 'Sublimation', 'Custom'" )
    materials: List[str] = Field(default_factory=list, description="Materials used")
    techniques: List[str] = Field(default_factory=list, description="Techniques like laser cut, engraving, sublimation")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    customizable: bool = Field(True, description="Whether personalization is available")
    featured: bool = Field(False, description="Highlight on homepage")
    in_stock: bool = Field(True, description="Available for order")


class OrderItem(BaseModel):
    product_id: str
    title: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    personalization: Optional[str] = None


class Customer(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class Order(BaseModel):
    """
    Collection: order
    Stores a simple order with items and customer details
    """
    items: List[OrderItem]
    customer: Customer
    total_eur: float = Field(ge=0)
    status: str = Field(default="pending", description="pending|confirmed|fulfilled|cancelled")
