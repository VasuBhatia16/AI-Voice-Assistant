from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.voice import router as voice_router
# from fastapi.staticfiles import StaticFiles


app = FastAPI(title="AI Voice Assistant Backend")

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(voice_router, prefix="/api/v1/voice", tags=["Voice"])

@app.get("/")
async def root():
    return {"message": "Backend running successfully!"}
