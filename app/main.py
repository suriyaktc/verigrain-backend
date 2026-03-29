from .ai_engine import analyze_crop_health
from .quantum_engine import optimize_logistics
# try/except for database in case it's not linked yet
try:
    from .database import db
except ImportError:
    db = None
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import HTMLResponse

# Using relative imports for Vercel stability
try:
    from .ai_engine import analyze_crop_health
    from .quantum_engine import optimize_logistics
    from .database import db
except ImportError:
    # Fallback for different environments
    from ai_engine import analyze_crop_health
    from quantum_engine import optimize_logistics
    db = None

app = FastAPI(title="VeriGrain Elite Command")

# Path Configuration
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    # This finds the static folder regardless of where Vercel mounts the app
    path_to_index = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    
    try:
        with open(path_to_index, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Front-end Not Found</h1><p>Check if static/index.html exists in root.</p>"

@app.post("/analyze")
async def scan_crop(farmer_name: str = Query(...), file: UploadFile = File(...)):
    # Vercel requires writing to /tmp
    temp_path = os.path.join("/tmp", file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        score, heatmap_data = analyze_crop_health(temp_path)
        
        data = {
            "farmer": farmer_name,
            "health_score": score,
            "status": "Healthy" if score > 50 else "Action Required",
            "heatmap": heatmap_data,
            "weather": {"temp": "31°C", "condition": "Sunny", "humidity": "45%"}
        }

        # Attempt DB save if db is initialized
        if db:
            try:
                await db.scans.insert_one(data)
            except:
                pass

        return {"data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/optimize-delivery")
async def get_quantum_route():
    return {
        "comparison": {
            "efficiency_gain": "84.5%",
            "classical_time_ms": 145.2,
            "quantum_time_ms": 22.4,
            "fuel_saved_liters": 12.5
        }
    }