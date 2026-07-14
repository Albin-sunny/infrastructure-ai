
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool  # <-- Handles the concurrency upgrade
import os
import uuid
from pathlib import Path

from backend.app.services.report_generator import generate_report
from backend.app.rag.recommendation import get_repair_recommendation
from backend.app.services.detection import detect_crack, calculate_crack_area
from backend.app.database.database import get_db  # <-- Links to your safe dependency provider
from backend.app.database.inspection_model import Inspection

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def sync_write(file_bytes: bytes, target_path: str):
    """Helper utility executed inside background worker threads for safe disk writes."""
    with open(target_path, "wb") as buffer:
        buffer.write(file_bytes)


@router.post("/detect")
async def detect(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Enterprise-ready vision analytics gateway featuring loop-isolated thread pools
    and defensive storage cleanup safeguards.
    """
    
    MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 Megabytes Max
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail="Payload size footprint exceeds maximum 15MB infrastructure limits."
        )

    file_path = None
    try:
        extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        await run_in_threadpool(sync_write, file_bytes, file_path)

        results = await run_in_threadpool(detect_crack, file_path)

        
        count = len(results[0].boxes)
        crack_area_percent = float(await run_in_threadpool(calculate_crack_area, results))

        
        if count > 0:
            confidence = float(results[0].boxes.conf.max())
        else:
            confidence = 0.0

    
        if crack_area_percent >= 15:
            severity = "High"
        elif crack_area_percent >= 5:
            severity = "Medium"
        else:
            severity = "Low"

       
        if severity == "High":
            risk_level = "Requires Immediate Inspection"
        elif severity == "Medium":
            risk_level = "Monitor and Schedule Repair"
        else:
            risk_level = "Low Risk"

        # 4. Offload blocking network RAG calls and ReportLab compiler routines
        recommendation = await run_in_threadpool(
            get_repair_recommendation, severity, crack_area_percent
        )    

        pdf_path = os.path.join(REPORT_DIR, f"report_{uuid.uuid4().hex}.pdf")
        await run_in_threadpool(
            generate_report, 
            pdf_path, 
            count, 
            crack_area_percent, 
            severity, 
            risk_level, 
            recommendation
        )

        # 5. Build record entity model
        inspection = Inspection(
            defect_type="Concrete Crack",
            defect_count=count,
            severity=severity,
            image_path=file_path,
            crack_area_percent=crack_area_percent,
            repair_recommendation=recommendation,
            report_path=pdf_path
        )

        
        def save_records():
            db.add(inspection)
            db.commit()
            
        await run_in_threadpool(save_records)

        return {
            "status": "success",
            "model": "YOLOv8 Custom Trained Segmentation Model",
            "defect_type": "Concrete Crack",
            "defect_count": count,
            "crack_area_percent": crack_area_percent,
            "confidence": round(confidence, 2),
            "severity": severity,
            "risk_level": risk_level,
            "repair_recommendation": recommendation,
            "report_path": pdf_path,
            "image_path": file_path
        }

    except Exception as e:
        await run_in_threadpool(db.rollback)
        
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=500,
            detail=f"Vision Inference Processing Pipeline Aborted: {str(e)}"
        )