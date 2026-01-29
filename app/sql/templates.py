from __future__ import annotations
from typing import Tuple


# HS-level views
VIEW_EXPORT = "public.v_export_monthly_hs"
VIEW_EXPORT_COMPANY = "public.v_export_company_monthly_hs"
VIEW_IMPORT = "public.v_import_monthly_hs"

# Category-level views
VIEW_IMPORT_CATEGORY = "public.v_import_monthly_category"
# (ирээдүйд хэрэгтэй бол)
# VIEW_EXPORT_CATEGORY = "public.v_export_monthly_category"


def _need_category(filters: dict | None) -> bool:
    if not filters:
        return False
    return any(filters.get(k) for k in ("purpose", "sub1", "sub2", "sub3"))


def resolve_view(
    domain: str,
    need_company: bool,
    filters: dict | None = None,
) -> Tuple[str, str]:
    """
    Returns: (view_name, view_type)
    view_type: "hs" | "category"
    """
    need_category = _need_category(filters)

    if domain == "import":
        if need_category:
            return VIEW_IMPORT_CATEGORY, "category"
        return VIEW_IMPORT, "hs"

    # export
    if need_company:
        return VIEW_EXPORT_COMPANY, "hs"

    # Future hook:
    # if need_category:
    #     return VIEW_EXPORT_CATEGORY, "category"

    return VIEW_EXPORT, "hs"
