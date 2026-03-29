from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile, File, Query
from app.database import db
from app.ai_engine import analyze_crop_health
from app.quantum_engine import optimize_logistics
import shutil
import os

app = FastAPI(title="VeriGrain AI-Quantum Backend")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.get("/")
async def root():
    return {"message": "VeriGrain Backend is Live!"}

@app.post("/analyze")
async def scan_crop(
    farmer_name: str = Query(...), 
    file: UploadFile = File(...)
):
    temp_path = f"temp_{file.filename}"
    try:
        # 1. Save and Process
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        score = analyze_crop_health(temp_path)
        status = "Healthy" if score > 60 else "Action Required"

        scan_record = {
            "farmer": farmer_name,
            "filename": file.filename,
            "health_score": score,
            "status": status,
            "location": {"lat": 12.9, "lon": 80.1},
            "timestamp": "2026-03-29T15:00:00" 
        }
        
        # 2. Database Protection
        try:
            await db.scans.insert_one(scan_record)
            db_status = "Saved to Cloud"
        except Exception as e:
            db_status = f"Database Offline, but scan complete. Error: {str(e)}"

        return {
            "db_status": db_status,
            "data": scan_record
        }

    finally:
        # Always clean up the file even if it crashes
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/optimize-delivery")
async def get_quantum_route():
    try:
        cursor = db.scans.find({"status": "Action Required"})
        critical_farms = await cursor.to_list(length=10)
        
        if not critical_farms:
            # If DB is empty, use mock data so you can still show the Quantum demo!
            critical_farms = [{"id": "mock1"}, {"id": "mock2"}]

        quantum_result = optimize_logistics(critical_farms)
        return {
            "status": "Optimization Complete",
            "source": "Database" if len(critical_farms) > 2 else "Mock (DB Empty)",
            "result": quantum_result
        }
    except Exception as e:
        return {"error": f"Quantum route failed: {str(e)}"}
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("static/index.html", "r") as f:
        return f.read()