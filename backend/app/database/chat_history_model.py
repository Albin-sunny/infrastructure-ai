from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func
from backend.app.database.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)

    conversation_id = Column(Text)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )