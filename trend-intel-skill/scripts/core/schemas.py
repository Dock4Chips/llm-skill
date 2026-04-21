from dataclasses import dataclass, field
from typing import List


@dataclass
class TrendItem:
    title: str
    url: str
    description: str
    language: str
    stars: str
    forks: str


@dataclass
class TrendSection:
    title: str
    items: List[TrendItem] = field(default_factory=list)
    is_subsection: bool = False


@dataclass
class PlatformReport:
    platform: str
    filename: str
    date: str
    sections: List[TrendSection] = field(default_factory=list)
