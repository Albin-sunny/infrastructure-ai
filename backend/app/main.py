from fastapi import FastAPI
from backend.app.api.detect import router as detect_router
from backend.app.api.chat import router as chat_router

app = FastAPI()

app.include_router(detect_router)
app.include_router(chat_router)

@app.get("/")
def home():
    return {
        "message": "InfraGuard AI Running"
    }