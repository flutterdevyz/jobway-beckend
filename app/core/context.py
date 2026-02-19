import contextvars
from typing import Optional

# ContextVar to store the base URL (e.g., http://10.31.74.7:8080)
request_base_url: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_base_url", default=None)

def get_base_url() -> Optional[str]:
    return request_base_url.get()

def set_base_url(url: str) -> None:
    request_base_url.set(url)
