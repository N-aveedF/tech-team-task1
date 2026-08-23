from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
import sqlite3
import hashlib
import time
from datetime import datetime

app = FastAPI()
DB = "url_shortener.db"

# Initialize Database
with sqlite3.connect(DB) as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS urls (short TEXT PRIMARY KEY, orig TEXT, exp TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS stats (short TEXT, time TEXT)")

# Dictionary to store IP addresses and timestamps for Rate Limiting
rate_limit_db = {}

class URLReq(BaseModel):
    url: str
    alias: str | None = None
    exp: str | None = None

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("index.html", "r") as file:
        return file.read()

@app.post("/shorten")
def shorten(req: URLReq, request: Request):
    # Get IP (Fallback to "local" if it struggles to read localhost)
    client_ip = request.client.host if request.client else "local"
    now = time.time()
    
    if client_ip not in rate_limit_db:
        rate_limit_db[client_ip] = []
        
    # Remove timestamps older than 60 seconds
    rate_limit_db[client_ip] = [t for t in rate_limit_db[client_ip] if now - t < 60]
    
    # --- DEBUGGING PRINT ---
    print(f"👉 Request attempt from {client_ip} | Current count in last 60s: {len(rate_limit_db[client_ip])}")
    
    # Block if 5 or more exist
    if len(rate_limit_db[client_ip]) >= 5:
        print("🚨 RATE LIMIT TRIGGERED!")
        raise HTTPException(429, "Rate limit exceeded: You can only create 5 links per minute.")
        
    # Add current request timestamp
    rate_limit_db[client_ip].append(now)

    # Core Logic
    if not req.url.startswith(("http://", "https://")):
        raise HTTPException(400, "Invalid URL format. Must start with http:// or https://")
        
    short = req.alias or hashlib.md5(req.url.encode()).hexdigest()[:6]
    
    try:
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO urls VALUES (?, ?, ?)", (short, req.url, req.exp))
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Alias or short code already in use")
        
    return {"short_url": f"http://localhost:8000/{short}", "short_code": short, "expires": req.exp}

@app.get("/{short}")
def redirect(short: str):
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT orig, exp FROM urls WHERE short = ?", (short,)).fetchone()
        if not row:
            raise HTTPException(404, "Short URL not found")
        if row[1] and datetime.now() > datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"):
            raise HTTPException(410, "This URL has expired")
            
        conn.execute("INSERT INTO stats VALUES (?, ?)", (short, datetime.now().isoformat()))
        return RedirectResponse(row[0])

@app.get("/analytics/{short}")
def analytics(short: str):
    with sqlite3.connect(DB) as conn:
        visits = conn.execute("SELECT time FROM stats WHERE short = ?", (short,)).fetchall()
        if not visits:
            raise HTTPException(404, "Analytics not found for this short code")
        return {"short_code": short, "total_visits": len(visits), "history": [v[0] for v in visits]}
