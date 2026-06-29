from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from backend.app.services.report_generator import generate_report
import uuid
from pathlib import Path

from backend.app.rag.recommendation import (
    get_repair_recommendation
)


from backend.app.services.detection import (
    detect_crack,
    calculate_crack_area
)

from backend.app.database.database import SessionLocal
from backend.app.database.inspection_model import Inspection

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@router.post("/detect")
async def detect(file: UploadFile = File(...)):

    db = SessionLocal()

    try:

        extension = Path(file.filename).suffix

        unique_filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        file_path = os.path.join(
            UPLOAD_DIR,
            unique_filename
        )

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Run YOLO Detection
        results = detect_crack(file_path)

        # Crack Count
        count = len(results[0].boxes)

        # Crack Area Percentage
        crack_area_percent = float(calculate_crack_area(results))

        # Confidence
        if count > 0:
            confidence = float(
                results[0].boxes.conf.max()
            )
        else:
            confidence = 0.0

        # Area-Based Severity
        if crack_area_percent >= 15:
            severity = "High"

        elif crack_area_percent >= 5:
            severity = "Medium"

        else:
            severity = "Low"

        # Risk Level
        if severity == "High":
            risk_level = "Requires Immediate Inspection"

        elif severity == "Medium":
            risk_level = "Monitor and Schedule Repair"

        else:
            risk_level = "Low Risk"

        # RAG Recommendation
        recommendation = get_repair_recommendation(
            severity,
            crack_area_percent
        )    

        pdf_path = os.path.join(
            REPORT_DIR,
            f"report_{uuid.uuid4().hex}.pdf"
        )

        generate_report(
            pdf_path,
            count,
            crack_area_percent,
            severity,
            risk_level,
            recommendation
        )

        # Save Inspection
        inspection = Inspection(
            defect_type="Concrete Crack",
            defect_count=count,
            severity=severity,
            image_path=file_path,
            crack_area_percent=crack_area_percent,
            repair_recommendation=recommendation,
            report_path=pdf_path
            
        )

        db.add(inspection)
        db.commit()

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

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()