from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")

SYSTEM_PROMPT = """
Та зөвхөн өгөгдсөн баримтуудаас хариул.

Дүрэм:
1. Тоон мэдээлэл байвал яг эх файлаас ав.
2. Олдохгүй бол "файлд олдсонгүй" гэж хэл.
3. Таамаг бүү хий.
4. Боломжтой бол эх сурвалжийг дурд.
5. Хариултаа товч, тодорхой, ойлгомжтой өг.
6. Хэрэв хэрэглэгч харьцуулалт, өсөлт, бууралтын талаар асуувал файлуудаас байгаа тоон мэдээлэлд тулгуурлан тайлбарла.
7. Хэрэв нэгээс олон файлд холбоотой асуулт байвал холбогдох бүх мэдээллийг нэгтгэн хариул.
"""

class KnowledgeChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def knowledge_chat(body: KnowledgeChatRequest):
    if not VECTOR_STORE_ID:
        raise HTTPException(status_code=500, detail="OPENAI_VECTOR_STORE_ID missing")

    resp = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": body.message,
            },
        ],
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
            }
        ],
    )

    return {
        "answer": resp.output_text
    }