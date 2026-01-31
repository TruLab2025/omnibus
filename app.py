from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import uuid
from datetime import datetime
import os
from urllib.parse import urlparse, quote_plus
from parser import parse_price
from cron import run_cron

app = FastAPI(title="Price Tracker PoC")

# Mount static files with absolute path
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "tracked.json"
AFFILIATES_FILE = "affiliates.json"

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

class AffiliateRule(BaseModel):
    domain: str
    network: str
    template: str
    active: bool

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

def load_affiliates():
    if not os.path.exists(AFFILIATES_FILE):
        return {}
    with open(AFFILIATES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_affiliates(data):
    with open(AFFILIATES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return None

@app.post("/check")
async def check_url(request: CheckRequest):
    # ... (existing check_url logic) ...
    data = parse_price(request.url)
    
    # Handle blocked state
    if data and data.get("blocked"):
        return {
            "blocked": True,
            "warning": data.get("warning"),
            "status_code": data.get("status_code"),
            "current_price": 0,
            "lowest_30d": 0,
            "status": "gray",
            "savings": 0,
            "currency": "",
            "is_simulated": False
        }

    if not data or data.get("current_price") == 0:
        raise HTTPException(status_code=400, detail="Nie udało się pobrać ceny. Strona może być zablokowana lub URL jest niepoprawny.")
    
    current_price = data["current_price"]
    lowest_30d = data["lowest_30d_price"]
    
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

# ... (existing track_product logic) ...

# --- Affiliate Endpoints ---

@app.get("/out/{item_id}")
async def affiliate_redirect(item_id: str):
    tracked_items = load_data()
    item = next((i for i in tracked_items if i["id"] == item_id), None)
    
    if not item:
        # Fallback if item not found (sould handle error better in prod, but for MVP redirect to root)
        return RedirectResponse("/")
        
    original_url = item["url"]
    domain = get_domain(original_url)
    
    affiliates = load_affiliates()
    
    if domain in affiliates and affiliates[domain]["active"]:
        template = affiliates[domain]["template"]
        encoded_url = quote_plus(original_url)
        # Simple replacement
        affiliate_link = template.replace("{url}", encoded_url)
        return RedirectResponse(affiliate_link)
    
    # Fallback to original URL
    return RedirectResponse(original_url)

# --- Admin API ---

@app.get("/admin")
async def get_admin_panel():
    return FileResponse("admin.html")

@app.get("/admin/affiliates")
async def get_affiliates():
    return load_affiliates()

@app.post("/admin/affiliates")
async def update_affiliate(rule: AffiliateRule):
    affiliates = load_affiliates()
    affiliates[rule.domain] = {
        "network": rule.network,
        "template": rule.template,
        "active": rule.active
    }
    save_affiliates(affiliates)
    return {"status": "success", "message": f"Reguła dla {rule.domain} zaktualizowana"}

@app.delete("/admin/affiliates/{domain}")
async def delete_affiliate(domain: str):
    affiliates = load_affiliates()
    if domain in affiliates:
        del affiliates[domain]
        save_affiliates(affiliates)
        return {"status": "success", "message": "Reguła usunięta"}
    raise HTTPException(status_code=404, detail="Domena nie znaleziona")

# --- Existing Endpoints ---

@app.get("/")
async def get_frontend():
    return FileResponse("index.html")

@app.get("/new")
async def get_new_frontend():
    return FileResponse("new_frontend.html")

@app.get("/frontend.html")
async def get_frontend_direct():
    return FileResponse("frontend.html")

@app.get("/tracked")
async def get_tracked():
    return load_data()

@app.delete("/tracked/{item_id}")
async def delete_tracked(item_id: str):
    tracked_items = load_data()
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
