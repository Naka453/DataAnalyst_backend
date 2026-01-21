from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router

# ✅ Truststore: optional (dev/VPN дээр хэрэгтэй байж болно), production дээр байхгүй байсан ч асна
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

app = FastAPI(title="Trade Chatbot API", version="0.1.0")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)