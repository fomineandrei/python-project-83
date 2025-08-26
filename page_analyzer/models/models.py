from dataclasses import dataclass
from typing import Optional


@dataclass
class Url:
    id: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    last_check: Optional[str] = None
    status_code: Optional[str] = None


@dataclass
class UrlCheck:
    id: Optional[int] = None
    url_id: Optional[int] = None
    status_code: Optional[int] = None
    h1: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
