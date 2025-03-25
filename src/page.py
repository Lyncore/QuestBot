from dataclasses import dataclass


@dataclass
class Page[T]:
    page: int
    total_count: int
    items: [T]