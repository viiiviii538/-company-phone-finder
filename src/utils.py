import chardet
from typing import Optional


def detect_encoding(path: str) -> str:
    """Detect file encoding using chardet."""
    with open(path, "rb") as f:
        data = f.read(10000)
    result = chardet.detect(data)
    return result.get("encoding") or "utf-8"


def detect_encoding_bytes(data: bytes) -> str:
    """Detect encoding for raw bytes."""
    result = chardet.detect(data)
    return result.get("encoding") or "utf-8"
