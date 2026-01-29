# app/conversation/merge.py
from .models import ConversationState, Intent, Commodity

HS_LABEL_MAP = {
    "2701": "нүүрс",
    "2702": "нүүрс",
    "2603": "зэс",
    "2601": "Төмрийн хүдэр, баяжмал",
}


def merge_intent(
    prev: ConversationState,
    intent: Intent,
    overrides: dict,
) -> ConversationState:
    """
    Previous state + шинэ intent + follow-up override-уудыг нэгтгэнэ
    """
    s = prev.model_copy(deep=True)

    # --- base intent ---
    if intent.domain:
        s.domain = intent.domain

    if intent.metric:
        s.metric = intent.metric

    # base time from intent
    if intent.time:
        # ✅ years эхэлж (multi-year) → year-г clear
        if "years" in intent.time and intent.time["years"]:
            s.time.years = intent.time["years"]
            s.time.year = None
            s.time.latest = False

        # ✅ year → years-г clear
        if "year" in intent.time and intent.time["year"]:
            s.time.year = intent.time["year"]
            s.time.years = None
            s.time.latest = False

        # ✅ explicit latest (хэрвээ intent_extractor ингэж өгдөг бол)
        if intent.time == "latest" or (
                isinstance(intent.time, dict) and intent.time.get("latest") is True
        ):
            s.time.latest = True
            s.time.year = None
            s.time.years = None

    # commodity (HS → label)
    filters = intent.filters or {}
    hs = filters.get("hscode")
    has_category = any(filters.get(k) for k in ("purpose", "sub1", "sub2", "sub3"))

    # ✅ category асуулт ирвэл HS commodity-г цэвэрлэнэ (8703 risk-ийг бууруулна)
    if has_category:
        s.commodity = None

    # ✅ HS ирсэн үед л commodity set хийнэ (list / string-safe)
    elif hs:
        hs_list = hs if isinstance(hs, list) else [hs]
        hs_list = [str(x).strip() for x in hs_list if str(x).strip()]
        if hs_list:
            label = HS_LABEL_MAP.get(hs_list[0], f"HS {hs_list[0]}")
            s.commodity = Commodity(label=label, hscode=hs_list)

    # -----------------------
    # follow-up overrides
    # -----------------------

    # ✅ granularity (сар/жил)
    if overrides.get("granularity"):
        s.time.granularity = overrides["granularity"]

    # ✅ time overrides MUST be independent of granularity
    if overrides.get("year"):
        s.time.year = overrides["year"]
        s.time.years = None
        s.time.latest = False

    if overrides.get("years"):
        s.time.years = overrides["years"]
        s.time.year = None
        s.time.latest = False

    if overrides.get("latest") is True:
        s.time.latest = True
        s.time.year = None
        s.time.years = None

    # scale
    if overrides.get("scale_label"):
        s.scale_label = overrides["scale_label"]

    # metric/unit
    if overrides.get("metric"):
        s.metric = overrides["metric"]

    if overrides.get("unit"):
        s.unit = overrides["unit"]

    return s


def apply_compare_prev_year(s: ConversationState) -> ConversationState:
    """
    “өмнөх онтой харьцуулах” гэвэл
    """
    out = s.model_copy(deep=True)

    if isinstance(out.time.year, int) and out.time.year >= 1900 and not out.time.years:
        out.time.years = [out.time.year - 1, out.time.year]
        out.time.year = None
        out.time.latest = False

    return out