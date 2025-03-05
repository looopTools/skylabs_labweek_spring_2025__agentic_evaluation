from typing import Generic, Optional, Sequence, TypeVar
from pydantic import BaseModel
from fastapi import Query

T = TypeVar("T")

class PageParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

class Page(BaseModel, Generic[T]):
    """Pagination response model"""
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PageParams) -> "Page[T]":
        pages = (total + params.size - 1) // params.size
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
            has_next=params.page < pages,
            has_prev=params.page > 1
        )