from fastapi import APIRouter, HTTPException
from backend.app.api.chat_schema import ChatRequest
from backend.app.rag.generate_answer import generate_answer

from backend.app.database.database import SessionLocal
from backend.app.database.chat_history_model import ChatHistory

router = APIRouter()

@router.post("/inspection-chat")
async def inspection_chat(request: ChatRequest):

    db = SessionLocal()

    try:

        history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.conversation_id
                == request.conversation_id
            )
            .order_by(ChatHistory.id.desc())
            .limit(10)
            .all()
        )

        history_text = ""

        for chat in reversed(history):

            history_text += (
                f"User: {chat.question}\n"
                f"Assistant: {chat.answer}\n\n"
            )

        answer = generate_answer(
            request.question,
            history_text
        )

        chat = ChatHistory(
    conversation_id=request.conversation_id,
            question=request.question,
            answer=answer
        )

        db.add(chat)
        db.commit()

        return {
            "status": "success",
            "question": request.question,
            "answer": answer
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()