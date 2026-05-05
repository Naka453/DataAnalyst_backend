from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.intent_router import detect_intent


def test_trade_amount_question_routes_to_sql_not_rag():
    assert detect_intent("2026 оны нийт экспортын үнийн дүн хэд вэ") == "sql"


def test_trade_import_quantity_question_routes_to_sql_not_rag():
    assert detect_intent("2026 оны импортын тоо хэмжээ хэд вэ") == "sql"


def test_pdf_style_transport_question_still_routes_to_rag():
    assert detect_intent("2026 оны ачаа тээврийн тайлангийн мэдээ") == "rag"
