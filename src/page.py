from dataclasses import dataclass


@dataclass
class Page:
    page: int
    total_count: int
    items: []