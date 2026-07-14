
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool  # <-- Prevents event loop freezing

from backend.app.api.chat_schema import ChatRequest
from backend.app.rag.generate_answer import generate_answer
from backend.app.database.database import get_db  # <-- Clean dependency provider
from backend.app.database.chat_history_model import ChatHistory

router = APIRouter()

@router.post("/inspection-chat")
async def inspection_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Production-grade engineering chat engine featuring secure dependency 
    injection and threadpool isolation for network and database operations.
    """
    try:
        
        def fetch_history():
            return (
                db.query(ChatHistory)
                .filter(ChatHistory.conversation_id == request.conversation_id)
                .order_by(ChatHistory.id.desc())
                .limit(10)
                .all()
            )
        
        history = await run_in_threadpool(fetch_history)

        
        history_text = ""
        for chat in reversed(history):
            history_text += (
                f"User: {chat.question}\n"
                f"Assistant: {chat.answer}\n\n"
            )

        
        answer = await run_in_threadpool(generate_answer, request.question, history_text)

        
        chat_record = ChatHistory(
            conversation_id=request.conversation_id,
            question=request.question,
            answer=answer
        )

    
        def commit_record():
            db.add(chat_record)
            db.commit()
            db.refresh(chat_record)
            
        await run_in_threadpool(commit_record)

        return {
            "status": "success",
            "question": request.question,
            "answer": answer
        }

    except Exception as e:
        
        await run_in_threadpool(db.rollback)
        raise HTTPException(
            status_code=500,
            detail=f"Chat Execution Pipeline Failed: {str(e)}"
        )

    
