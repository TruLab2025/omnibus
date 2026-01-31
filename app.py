from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime
import os
from parser import parse_price
from cron import run_cron

app = FastAPI(title="Price Tracker PoC")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "tracked.json"

class CheckRequest(BaseModel):
    url: str

class TrackRequest(BaseModel):
    url: str
    email: str
    current_price: float
    lowest_30d: float
    status: str
    title: Optional[str] = None
    image_url: Optional[str] = None

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.post("/check")
async def check_url(request: CheckRequest):
    data = parse_price(request.url)
    if not data or data.get("current_price") == 0:
        raise HTTPException(status_code=400, detail="Nie udało się pobrać ceny. Strona może być zablokowana lub URL jest niepoprawny.")
    
    current_price = data["current_price"]
    lowest_30d = data["lowest_30d_price"]
    
    # Verdict logic
    if current_price < lowest_30d:
        status = "green"
    elif current_price == lowest_30d:
        status = "yellow"
    else:
        status = "red"
        
    savings = lowest_30d - current_price
    
    return {
        "current_price": current_price,
        "lowest_30d": lowest_30d,
        "status": status,
        "savings": savings,
        "currency": data["currency"],
        "is_simulated": data.get("is_simulated", False),
        "warning": data.get("warning"),
        "title": data.get("title"),
        "description": data.get("description"),
        "image_url": data.get("image_url")
    }

@app.post("/track")
async def track_product(request: TrackRequest):
    tracked_items = load_data()
    
    new_entry = {
        "id": str(uuid.uuid4()),
        "url": request.url,
        "email": request.email,
        "title": request.title or "Produkt",
        "image_url": request.image_url,
        "price_at_add": request.current_price,
        "last_known_price": request.current_price,
        "lowest_30d": request.lowest_30d,
        "currency": "PLN",
        "status": request.status,
        "created_at": datetime.now().isoformat(),
        "last_checked": datetime.now().isoformat()
    }
    
    tracked_items.append(new_entry)
    save_data(tracked_items)
    
@app.get("/")
async def get_frontend():
    return FileResponse("frontend.html")

@app.get("/frontend.html")
async def get_frontend_direct():
    return FileResponse("frontend.html")

@app.get("/tracked")
async def get_tracked():
    return load_data()

@app.delete("/tracked/{item_id}")
async def delete_tracked(item_id: str):
    tracked_items = load_data()
    # Filter out the item to delete
    updated_items = [item for item in tracked_items if item["id"] != item_id]
    
    if len(updated_items) == len(tracked_items):
        raise HTTPException(status_code=404, detail="Produkt nie został znaleziony")
        
    save_data(updated_items)
    return {"status": "success", "message": "Produkt został usunięty"}

@app.post("/run-check")
async def run_batch_check():
    run_cron()
    return {"status": "success", "message": "Batch check completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
