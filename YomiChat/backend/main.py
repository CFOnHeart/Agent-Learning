from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agents import chat_agent
import json

app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Empty message")
    reply = chat_agent.chat(req.message)
    return ChatResponse(reply=reply)

@app.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Empty message")
    
    def generate():
        for chunk in chat_agent.chat_stream(req.message):
            # Send Server-Sent Events format
            data = json.dumps({"content": chunk, "type": "chunk"})
            yield f"data: {data}\n\n"
        
        # Send end signal
        end_data = json.dumps({"content": "", "type": "end"})
        yield f"data: {end_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

# 启动服务器
if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("uvicorn not found. Please install it with: pip install uvicorn[standard]")
        print("Or run manually with: uvicorn main:app --reload --port 8000")
