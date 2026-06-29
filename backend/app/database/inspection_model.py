from sqlalchemy import Column, Integer, String, Text, TIMESTAMP,Float
from sqlalchemy.sql import func
from backend.app.database.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    defect_type = Column(String(50))
    defect_count = Column(Integer)
    severity = Column(String(20))
    image_path = Column(Text)
    crack_area_percent = Column(Float, nullable=True)
    repair_recommendation = Column(Text)
    report_path = Column(Text)
    