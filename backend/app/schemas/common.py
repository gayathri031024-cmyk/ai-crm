from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


def build_pagination_meta(total: int, page: int, page_size: int) -> PaginationMeta:
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages)
