from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")

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
                "content": (
                    "Та зөвхөн хэрэглэгчийн оруулсан баримтууд дээр тулгуурлаж хариул. "
                    "Тоон мэдээлэл байвал яг эх баримтаас ав. "
                    "Олдохгүй бол 'файлд олдсонгүй' гэж хэл. "
                    "Таамаг бүү хий."
                ),
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