import os
import uuid
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict

app = FastAPI(title="ConsciousStream")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions_db = {}

class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.current_task = "الرئيسية"
        self.messages = []

class ChatRequest(BaseModel):
    session_id: str
    message: str
    task_id: Optional[str] = None

class CreateSessionRequest(BaseModel):
    goal_text: str = "جلسة عامة"

def get_reply(message: str) -> str:
    msg = message.lower()
    
    if "مرحبا" in msg or "السلام" in msg or "اهلا" in msg:
        return "👋 وعليكم السلام! أنا ConsciousStream، مساعدك الذكي. كيف يمكنني مساعدتك؟"
    
    if "كيف" in msg and "حال" in msg:
        return "😊 أنا بخير، شكراً! وأنت؟ أخبرني ماذا تحتاج؟"
    
    if "شكر" in msg:
        return "🙏 العفو! هذا واجبي. هل هناك شيء آخر؟"
    
    if "اسم" in msg or "من انت" in msg:
        return "🧠 اسمي ConsciousStream! أنا صديقك الذكي للمحادثات."
    
    if "قصة" in msg or "رواية" in msg:
        return "📖 أحب القصص! لنصنع قصة معاً. اختر نوعاً: خيال علمي، غموض، أو مغامرات؟"
    
    if "مهمة" in msg:
        return "📋 أنت في مهمة: 'الرئيسية'. استخدم /new اسم_المهمة لإنشاء مهمة جديدة."
    
    replies = [
        "💡 فهمت! دعنا نتعمق أكثر في هذا الموضوع.",
        "🎯 تمام! سجلت ملاحظاتك. ماذا بعد؟",
        "🧠 فكرة ممتازة! كيف ترغب في متابعتها؟",
        "📝 شكراً على هذه الإضافة. هل هناك تفاصيل أخرى؟",
        "🌟 رائع! هذا يفتح آفاقاً جديدة للنقاش.",
    ]
    return random.choice(replies)

@app.post("/api/sessions")
async def create_session(req: CreateSessionRequest):
    session_id = str(uuid.uuid4())
    sessions_db[session_id] = Session(session_id)
    return {"session_id": session_id}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    session = sessions_db.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
    
    if req.task_id:
        session.current_task = req.task_id
    
    session.messages.append({
        "role": "user",
        "content": req.message,
        "timestamp": datetime.now().isoformat()
    })
    
    reply = get_reply(req.message)
    
    session.messages.append({
        "role": "assistant",
        "content": reply,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"response": reply, "current_task": session.current_task}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "sessions": len(sessions_db)}

@app.get("/")
async def root():
    return {"message": "🧠 ConsciousStream API is running", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
