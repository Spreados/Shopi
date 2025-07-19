from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.petstore
products_collection = db.products
orders_collection = db.orders
cart_collection = db.carts

# Pydantic models
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    category: str
    features: List[str]
    image_url: str
    images: List[str]
    rating: float
    reviews_count: int
    in_stock: bool
    discount_percentage: Optional[int] = None

class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Cart(BaseModel):
    session_id: str
    items: List[CartItem]
    total: float
    created_at: datetime
    updated_at: datetime

class Order(BaseModel):
    id: str
    session_id: str
    items: List[CartItem]
    total: float
    customer_info: dict
    status: str
    created_at: datetime

# Initialize products data
def init_products():
    if products_collection.count_documents({}) == 0:
        products = [
            {
                "id": str(uuid.uuid4()),
                "name": "Steam Cat Brush - Professional Grooming Tool",
                "description": "Revolutionary steam-powered cat brush that gently removes loose fur while providing a soothing spa-like experience. The gentle steam helps to moisturize your cat's skin and makes grooming easier and more enjoyable for both you and your feline friend.",
                "price": 49.99,
                "original_price": 79.99,
                "category": "grooming",
                "features": [
                    "Steam-powered grooming technology",
                    "Gentle on sensitive cat skin",
                    "Removes 95% of loose fur",
                    "Reduces shedding significantly",
                    "Easy-to-clean design",
                    "Safe and comfortable for cats",
                    "Battery powered - cordless operation"
                ],
                "image_url": "https://images.unsplash.com/photo-1747176779062-4e800093611e",
                "images": [
                    "https://images.unsplash.com/photo-1747176779062-4e800093611e"
                ],
                "rating": 4.8,
                "reviews_count": 324,
                "in_stock": True,
                "discount_percentage": 38
            },
            {
                "id": str(uuid.uuid4()),
                "name": "3-in-1 Pet Bowl with Automatic Water Feeder",
                "description": "The ultimate feeding solution for your pets! This innovative 3-in-1 system combines a food bowl, water bowl, and automatic water dispenser in one sleek design. Perfect for cats and small dogs, ensuring your pet always has fresh water available.",
                "price": 34.99,
                "original_price": 59.99,
                "category": "feeding",
                "features": [
                    "3-in-1 design: food bowl + water bowl + dispenser",
                    "Automatic water refill system",
                    "Non-slip base for stability",
                    "Easy to clean and refill",
                    "Food-grade materials",
                    "Perfect height for cats and small dogs",
                    "1.5L water capacity"
                ],
                "image_url": "https://images.unsplash.com/photo-1695023267262-7f4ab64152b2",
                "images": [
                    "https://images.unsplash.com/photo-1695023267262-7f4ab64152b2",
                    "https://images.unsplash.com/photo-1670361921890-2eb8045a6411",
                    "https://images.unsplash.com/photo-1691130340089-bf83873e89ab"
                ],
                "rating": 4.6,
                "reviews_count": 187,
                "in_stock": True,
                "discount_percentage": 42
            }
        ]
        products_collection.insert_many(products)

# API Routes
@app.on_event("startup")
async def startup_event():
    init_products()

@app.get("/api/products")
async def get_products(category: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category
    
    products = list(products_collection.find(query, {"_id": 0}))
    return {"products": products}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = products_collection.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/cart/{session_id}")
async def get_cart(session_id: str):
    cart = cart_collection.find_one({"session_id": session_id}, {"_id": 0})
    if not cart:
        return {"session_id": session_id, "items": [], "total": 0}
    return cart

@app.post("/api/cart/{session_id}/add")
async def add_to_cart(session_id: str, product_id: str, quantity: int = 1):
    # Get product details
    product = products_collection.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get or create cart
    cart = cart_collection.find_one({"session_id": session_id})
    if not cart:
        cart = {
            "session_id": session_id,
            "items": [],
            "total": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    # Check if item already exists in cart
    item_found = False
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item_found = True
            break
    
    if not item_found:
        cart["items"].append({
            "product_id": product_id,
            "quantity": quantity,
            "price": product["price"]
        })
    
    # Recalculate total
    cart["total"] = sum(item["quantity"] * item["price"] for item in cart["items"])
    cart["updated_at"] = datetime.now()
    
    # Update in database
    cart_collection.replace_one(
        {"session_id": session_id}, 
        cart, 
        upsert=True
    )
    
    # Return cart without _id field
    cart_response = cart.copy()
    cart_response.pop("_id", None)  # Remove _id if it exists
    
    return {"message": "Item added to cart", "cart": cart_response}

@app.put("/api/cart/{session_id}/update")
async def update_cart_item(session_id: str, product_id: str, quantity: int):
    cart = cart_collection.find_one({"session_id": session_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if quantity <= 0:
        cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    else:
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                break
    
    # Recalculate total
    cart["total"] = sum(item["quantity"] * item["price"] for item in cart["items"])
    cart["updated_at"] = datetime.now()
    
    cart_collection.replace_one({"session_id": session_id}, cart)
    
    # Return cart without _id field
    cart_response = cart.copy()
    cart_response.pop("_id", None)  # Remove _id if it exists
    
    return {"message": "Cart updated", "cart": cart_response}

@app.delete("/api/cart/{session_id}/remove/{product_id}")
async def remove_from_cart(session_id: str, product_id: str):
    cart = cart_collection.find_one({"session_id": session_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    cart["total"] = sum(item["quantity"] * item["price"] for item in cart["items"])
    cart["updated_at"] = datetime.now()
    
    cart_collection.replace_one({"session_id": session_id}, cart)
    return {"message": "Item removed from cart"}

@app.post("/api/orders")
async def create_order(order_data: dict):
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "session_id": order_data["session_id"],
        "items": order_data["items"],
        "total": order_data["total"],
        "customer_info": order_data["customer_info"],
        "status": "pending",
        "created_at": datetime.now()
    }
    
    orders_collection.insert_one(order)
    
    # Clear cart after order
    cart_collection.delete_one({"session_id": order_data["session_id"]})
    
    return {"message": "Order created successfully", "order_id": order_id}

@app.get("/")
async def root():
    return {"message": "PetStore API is running"}