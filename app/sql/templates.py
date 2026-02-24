from typing import Dict, Optional, Tuple

# HS-level views
VIEW_EXPORT = "public.v_export_monthly_hs"
VIEW_EXPORT_COMPANY = "public.v_export_company_monthly_hs"
VIEW_IMPORT = "public.v_import_monthly_hs"

# (Category-level views now unused)
VIEW_IMPORT_CATEGORY = "public.v_import_monthly_category"

def _need_category(filters: Optional[dict]) -> bool:
    if not filters:
        return False
    return any(filters.get(k) for k in ("purpose", "sub1", "sub2", "sub3"))

def resolve_view(
        domain: str,
        need_company: bool,
        filters: Optional[dict] = None,
) -> Tuple[str, str]:
    """
    Returns: (view_name, view_type)
    view_type: "hs" | "category"
    """
    need_category = _need_category(filters)

    # Check if 'question' exists in filters
    question = filters.get("question", "")  # Get 'question' from filters
    print(f"Checking filters, question: {question}")  # Debugging line to verify filters content

    # For "import" domain, resolve view accordingly
    if domain == "import":
        if "импорт улсаар" in question:  # Check if "импорт улсаар" exists in the question
            print("Detected 'импорт улсаар' in the question")
            return "public.v_import_by_country", "hs"  # Use the appropriate view for 'timeseries_country'

        if need_category:
            return VIEW_IMPORT, "category"  # Previously was VIEW_IMPORT_CATEGORY
        return VIEW_IMPORT, "hs"

    # For export domain
    if domain == "export":
        if need_company:
            return VIEW_EXPORT_COMPANY, "hs"
        return VIEW_EXPORT, "hs"

    return "default_view", "hs"

