def detect_intent(message: str) -> str:
    text = (message or "").casefold().strip()

    trade_terms = [
        "экспорт", "импорт", "худалдаа", "гадаад худалдаа",
    ]
    analytic_terms = [
        "дүн", "үнийн дүн", "нийт", "нийлбэр", "хэд", "хэчнээн",
        "тоо хэмжээ", "хэмжээ", "тонн", "ам.доллар", "usd", "$",
        "нэгж үнэ", "дундаж", "өссөн", "өмнөх", "мөн үе", "yoy",
        "сараар", "сар сараар", "жилээр", "харьцуул",
    ]

    # Trade statistics questions must go through the SQL path.
    # Otherwise words like "экспорт" and "импорт" incorrectly route to PDF/RAG.
    if any(term in text for term in trade_terms) and (
        any(term in text for term in analytic_terms) or any(ch.isdigit() for ch in text)
    ):
        return "sql"

    keywords_rag = [
        "боомт", "хил", "орсон", "гарсан", "нэвтэрсэн",
        "зорчигч", "зорчсон", "жуулчин", "жуулчид", "иргэншил", "улсаар", "улс",
        "аялал", "аялал жуулчлал", "tourism", "tourist",
        "тээвэр", "тээврийн", "зам", "автотээвэр", "төмөр зам", "агаарын",
        "агаар", "нислэг", "нисэх", "road", "rail", "transport",
        "ачаа", "карго", "cargo", "дамжин", "дотоод",
        "тайлан", "статистик", "салбар", "мэдээ",
        "эрчим хүч", "цахилгаан", "дулаан", "үйлдвэрлэл", "станц", "дцс",
        "уцс", "сцс", "нцс", "сэргээгдэх", "энерги", "energy", "power",
    ]

    if any(keyword in text for keyword in keywords_rag):
        return "rag"

    return "sql"
